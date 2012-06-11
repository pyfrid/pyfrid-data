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

import numpy as np

from pyfrid.modules.plot.plot2d import BasePlot2DModule
from pyfrid.modules.live.core.live import BaseLiveDisplayModule

class BaseLive2DModule(BaseLiveDisplayModule, BasePlot2DModule):
    
    def __init__(self, *args, **kwargs):
        super(BaseLive2DModule,self).__init__(*args, **kwargs)
        self.xlabel="detectors"
        self.ylabel="counts"
        
    def get_data(self, area=None):
        return np.asarray(self.detector_device.get_data())
    
    def call_shutdown(self):
        super(BaseLive2DModule,self).call_shutdown()
       
    def call_initialize(self):
        super(BaseLive2DModule,self).call_initialize()
        