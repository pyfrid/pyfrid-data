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

import re
import abc
from pyfrid.core import BaseModule
from pyfrid.core.signal import Signal
from pyfrid.modules.data.core.dataset import Dataset

class BaseDataModule(BaseModule):
     
    def __init__(self, *args, **kwargs):
        super(BaseDataModule,self).__init__(*args, **kwargs)
        self._dataset=Dataset(headers=self.app.devices())
        self._handlers=[]
        self._group_preset=False
        self._name_preset=False
        self._init_names()
        
        self.before_shoot_signal=Signal(self)
        self.before_after_signal=Signal(self)
    
    def _init_names(self):
        self._datagroup   = ""
        self._datagroup_comment = ""
        self._dataname    = ""
        self._datacomment = ""
    
    def initialize(self):
        self._init_names()
        
    def release(self):
        self._group_preset=False
        self._name_preset=False
            
    def register_handler(self, h):
        self._handlers.append(h)
    
    @property
    def datainfo(self):
        return {
            "name"    : self._dataname,
            "comment" : self._datacomment
        }
        
    @property
    def dataname(self):
        return self._dataname
    
    @property
    def datagroup(self):
        return self._datagroup
        
    @property
    def groupinfo(self):
        return {
            "group"         : self._datagroup,
            "comment"       : self._datagroup_comment
        }
    
    def validate_name(self, name, comment=""):
        if not re.match(r"[A-Za-z_]+[0-9]*",name):
            self.error("Data name is not regular. It can contain only letters, numbers and '_'")
            return False
        return True
    
    def validate_group(self, name, comment=""):
        if not re.match(r"[A-Za-z_]+[0-9]*",name):
            self.error("Group name is not regular. It can contain only letters, numbers and '_'")
            return False
        return True
    
    def set_dataname(self, name, comment="", **kwargs):
        if not self.validate_name(name, comment): return
        self._dataname=name
        self._datacomment=comment
        
    def set_datagroup(self, name, comment="", **kwargs):
        if not self.validate_group(name, comment): return
        self._datagroup=name
        self._datagroup_comment=comment
                           
    def status(self):
        return (("Data group",self._datagroup,""),
                ("Group comment",self._datagroup_comment,""),
                ("Data name",self._dataname,""),
                ("Data comment",self._datacomment,"")
               )
        
    def get_data(self, colname):
        return self._dataset[colname]
        
    def init_data(self, *args, **kwargs):
        self._dataset.clear(headers=False)
        #if not self._makedatapath(): return False
        for h in self._handlers:
            try:
                h.init_data(*args, **kwargs)
            except Exception, err:
                self.exception(err)
                raise
    
    def validate_data(self, *args, **kwargs):
        if not self._datagroup and not self._group_preset:
            self.error("Data group is empty...")
            return False
        if not self._dataname and not self._name_preset:
            self.error("Data name is empty...")
            return False
        return True
        
    def acquire_data(self, tm, *args, **kwargs):
        self.call_shoot(tm)
        positions=[obj.call_position() for _,obj in self.app.iterate_devices()]
        self._dataset.append(positions)
        for h in self._handlers:
            try:
                h.dump_data(*args, **kwargs)
            except Exception, err:
                self.exception(err)
                raise
    
    def close_data(self, *args, **kwargs):
        for h in self._handlers:
            try:
                h.close_data(*args, **kwargs)
            except Exception, err:
                self.exception(err)
        #self._dataset.clear()
        
    def call_shoot(self, tm, *args, **kwargs):
        if self.stopped: return
        self.shoot(tm)
        
    @abc.abstractmethod            
    def shoot(self,tm):
        pass
    