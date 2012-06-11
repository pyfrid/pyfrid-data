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

from pyfrid.webapp.core.router import BaseObjectWebRouter

class BasePlotModuleWebRouter(BaseObjectWebRouter):
                        
    def resize(self,handler,w,h):
        return self.obj.resize(w,h)
    
    def get_coordinates(self,handler,x,y):
        return self.obj.get_coordinates(x,y)
    
    def get_image(self,handler,id):
        return self.obj.get_image(id)
    
    def activate(self,handler):
        self.obj.enabled=True
        
    def deactivate(self,handler):
        self.obj.enabled=False
    
    def set_zoom(self, handler, x1, y1, x2, y2):
        x1,y1=self.obj.get_coordinates(x1,y1)
        x2,y2=self.obj.get_coordinates(x2,y2)
        self.obj.set_zoom(x1, y1, x2, y2)
        
    def clear_zoom(self, handler):
        self.obj.clear_zoom()
        
    def add_mask(self, handler, x1, y1, x2, y2):
        x1,y1=self.obj.get_coordinates(x1,y1)
        x2,y2=self.obj.get_coordinates(x2,y2)
        self.obj.add_mask(x1, y1, x2, y2)
        
    def clear_mask(self, handler):
        self.obj.clear_mask()
        
    def clear_last_mask(self, handler):
        self.obj.clear_last_mask()
        
    def set_settings(self,handler,settings=[]):
        self.obj.set_settings(settings)
        return self.get_settings(handler)
                    
    def get_settings(self,handler):
        return self.obj.get_settings()
        