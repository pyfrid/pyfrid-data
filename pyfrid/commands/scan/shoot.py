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

from pyfrid.commands.scan.core.scan import BaseScanCommand
from pyfrid.core import FloatSetting


class BaseShootCommand(BaseScanCommand):
    
    maxtime=FloatSetting(9999.99, limits=[0, None])
    
    def __init__(self, *args, **kwargs):
        super(BaseShootCommand,self).__init__(*args, **kwargs)

    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import FLOATCONST, INTCONST
        return ([FLOATCONST, INTCONST], 1, 1)
    
    def execute(self, tm, repeat):
        try:
            self.init_data()
            for _ in range(repeat):
                if self.stopped: break
                self.acquire_data(tm)
        finally:
            self.close_data()
            
    def validate(self, tm, repeat):
        if not self.validate_data(): return False
        if not (0<=tm<=self.maxtime):
            self.error("Shooting time is out of range [0, {0}]".format(self.maxtime))
            return False
        if repeat<=0:
            self.error("The number of shootings should be >0")
            return False
        return True
    
    def runtime(self, tm, repeat=1):
        return tm*repeat
    