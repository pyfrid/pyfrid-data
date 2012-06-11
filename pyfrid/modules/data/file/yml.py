#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import time
import re
from datetime import datetime

import yaml

from pyfrid.core import StringSetting, BoolSetting 
from pyfrid.modules.data.core.handler import BaseDataHandlerModule

def listdirs(folder):
    if not os.path.exists(folder):
        return []
    return [ name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

class BaseYamlDataModule(BaseDataHandlerModule):
    
    maindir= StringSetting("./experiments", fixed=True )
    yeardir  = BoolSetting( True )
    monthdir = BoolSetting( True )
    
    def __init__(self, *args, **kwargs):
        super(BaseYamlDataModule,self).__init__(*args,**kwargs)
        self._datapath=""
        self._datadir=""
        self._header={}
        self._steps=0
    
    def makedatapath(self):
        pathitems=[self.maindir]
        if self.yeardir:  pathitems.append(str(datetime.now().year))
        if self.monthdir: pathitems.append(str(datetime.now().month))
        pathitems.extend([self.data_module.datagroup])
        mainpath=os.path.join(*pathitems)
        filenums=[int(dn.rsplit('_',1)[1])
             for dn in listdirs(mainpath)
             if re.match(r"{0}_(\d+)".format(self.data_module.dataname),dn)]
        maxnum=max(filenums) if filenums else -1
        datadir="{0}_{1:d}".format(self.data_module.dataname, maxnum+1)        
        datapath=os.path.join(mainpath, datadir)
        if datapath and not os.path.exists(datapath):
            try:
                os.makedirs(datapath)
            except Exception,err:
                self.exception("Exception while creating datapath: {0}".format(err))
                self._datapath = ''
                self._datadir  = ''
                return False
        self._datapath = os.path.join(mainpath, datadir)
        self._datadir  = datadir
        return True
    
    def init_data(self, *args, **kwargs):
        if not self.makedatapath(): return False
        self._steps=0
        self._header={
           "instrument":self.app.projname,
           "created":time.asctime(),
           "group":self.data_module.datagroup,
           "data":self.data_module.datainfo,
           "user": self.app.auth_module.current_login,
        }
        self.dump_settings(self._datapath, self._datadir)
       
    def dump_devices(self, path, bname):
        fn=os.path.join(path,"{0}.dev".format(bname))
        self.info("Saving devices state to {0}".format(fn))
        stream=file(fn,"a")
        self._header["saved"]=time.asctime()
        yaml.safe_dump(self._header,stream,explicit_start=True,default_flow_style=False,indent=4)
        for _,devobj in self.app.iterate_devices():
            yaml.safe_dump({devobj.name:{
                                     "position":devobj.call_position(),
                                     "units":devobj.units,
                                     "status":devobj.call_status()
                                     }},stream,explicit_start=True,indent=4)
            try:
                func=getattr(devobj,"call_save")
            except AttributeError:
                pass
            else:
                func(path, "{0}_{1}".format(bname, devobj.name))
                   
    def dump_settings(self, path, bname):
        fn=os.path.join(path,"{0}.set".format(bname))
        self.info("Saving settings to {0}".format(fn))
        f=file(fn,"a")
        yaml.safe_dump(self._header,f,explicit_start=True,default_flow_style=False,indent=4)
        def dump(iterator):   
            for objname, obj in iterator():
                data={objname:[(name, getattr(obj, name), item.units) for name, item in obj.iterate_settings()]}
                yaml.safe_dump(data,stream=f,explicit_start=True,indent=4)
        dump(self.app.iterate_devices)
        dump(self.app.iterate_modules)
        dump(self.app.iterate_commands)
                
    def dump_data(self, *args, **kwargs):
        fn="{0}_{1}".format(self._datadir, self._steps)
        self.dump_devices(self._datapath,fn)
        self._steps+=1
        
    def close_data(self, *args, **kwargs):
        self.info("Closing data...")
                