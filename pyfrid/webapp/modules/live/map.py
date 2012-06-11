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

from pyfrid.webapp.modules.live.live import BaseLiveModuleWebRouter

class LiveMapModuleWebRouter(BaseLiveModuleWebRouter):
    
    def set_center(self, handler, x, y):
        x,y=self.obj.get_coordinates(x,y)
        self.obj.set_center(x, y)
        
    def reset_center(self, handler):
        self.obj.reset_center()

