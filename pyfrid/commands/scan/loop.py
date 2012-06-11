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
from pyfrid.commands.scan.core.nodes import DeviceStepNode, LoopDeviceStepNode, MainLoopDeviceStepNode
from pyfrid.commands.scan.core.nodes import LoopScanNode, MainLoopScanNode
from pyfrid.commands.scan.core.scan import BaseScanCommand
from pyfrid.modules.system.vm.core.vm import ValidateError

class BaseLoopScanCommand(BaseScanCommand):
    
    numthreads=2
    
    def __init__(self, *args, **kwargs):
        super(BaseLoopScanCommand,self).__init__(*args, **kwargs)
    
    def completions(self):
        return ([self.app.devices()],True)
            
    def execute(self, mainloop, *args, **kwargs):
        try:
            self.init_data()
            mainloop.scan(self, numthreads=self.numthreads, validate=False)
        finally:
            self.close_data()
        
    def validate(self, mainloop, *args, **kwargs):
        if not self.validate_data(): return False  
        try:
            mainloop.scan(self, numthreads=self.numthreads, validate=True)
        except ValidateError:
            return False
        return True
        
    def runtime(self, mainloop, *args, **kwargs):
        return mainloop.calc_runtime(self, self.numthreads)
    
    def grammar(self):
        from lepl import Or, Delayed
        from pyfrid.modules.system.vm.leplvm  import DEVICE, FLOATCONST, LSBR, RSBR, LBR, RBR
             
        main_dev_item    = DEVICE & FLOATCONST[4]
        loop_dev_item    = DEVICE & FLOATCONST[3]                          
        dev_node         = DEVICE & FLOATCONST[2]                          >DeviceStepNode
        
        loop_rule        = Or(loop_dev_item,
                              loop_dev_item &  LSBR & dev_node[1:] & RSBR) >LoopDeviceStepNode
                     
        main_loop_rule   = Or(main_dev_item,
                              main_dev_item & LSBR & dev_node[1:] & RSBR)  >MainLoopDeviceStepNode
                          
        factor=Delayed()
        
        nested_rule      = Or(loop_rule, 
                              loop_rule & LBR & factor & RBR)              >LoopScanNode
                              
        factor+=nested_rule[1:]
        
        scan_rule=Or(main_loop_rule, 
                     main_loop_rule & LBR & nested_rule & RBR)             >MainLoopScanNode
                         
        return ([scan_rule], 1, 1)
    