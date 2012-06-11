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

from pyfrid.webapp.core.router import authenticated
from pyfrid.webapp.modules.plot.plot import BasePlotModuleWebRouter
from pyfrid.webapp.core.objtree import BaseObjectTree

class InfoDeviceNode(object):
    
    def __init__(self,obj):
        self.obj=obj
        
    def __call__(self):
        return {
             "name": self.obj.name,
             "type": "device"
        }
     
class InfoGroupNode(list):
    
    def __init__(self,name):
        self.name=name
                
    def __call__(self):
        _children=[item() for item in self]
        children=filter(lambda x: bool(x),_children)
        return {         
            "name":     self.name,
            "children": children,
            "type":     "group"
        }
    
class InfoDeviceTree(BaseObjectTree):
    object_node=InfoDeviceNode
    group_node=InfoGroupNode

class Plot2DDataWebRouter(BasePlotModuleWebRouter):

    def __init__(self, *args, **kwargs):
        super(Plot2DDataWebRouter, self).__init__(*args, **kwargs)
        self.xaxis_info_tree  = InfoDeviceTree  (self, Plot2DDataWebRouter.xdev_menu_iterator, "X axis")
        self.yaxis_info_tree  = InfoDeviceTree  (self, Plot2DDataWebRouter.ydev_menu_iterator, "Y axis")
        
    def xdev_menu_iterator(self):
        for name, dev in self.obj.app.iterate_devices(permission=["view", "move"], byname=True):
            if dev.can("move"): yield name, dev
            
    def ydev_menu_iterator(self):
        for name, dev in self.obj.app.iterate_devices(permission=["view", "count"], byname=True):
            if dev.can("count"): yield name, dev
            
    def set_xdev(self, handler, name):
        with authenticated(handler, self.obj.app):
            dev=self.obj.app.get_device(name, byname=True, exc=True)
            self.obj.set_xdev(dev, update=True)
            
    def set_ydev(self, handler, name):
        with authenticated(handler, self.obj.app):
            dev=self.obj.app.get_device(name, byname=True, exc=True)
            self.obj.set_ydev(dev, update=True)
            
    def get_static_data(self):  
        return {
            "xdevinfo": self.xaxis_info_tree(),
            "ydevinfo": self.yaxis_info_tree()
        }  
        