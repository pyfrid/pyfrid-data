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
from pyfrid.core import BaseDevice
from pyfrid.devices.counters.core.counter import BaseAbstractCounterDevice, DataHandler2D
from pyfrid.core import FloatListSetting, BoolSetting

class BasePSDDevice(BaseAbstractCounterDevice):
    data_handler_class=DataHandler2D
    
    @property
    def size(self):
        return self._data_handler.size
    
    
class BaseROIDevice(BaseDevice):
    
    detector_device=None
    roi_on=BoolSetting(False)
    
    def __init__(self, *args, **kwargs):
        super(BaseROIDevice, self).__init__(*args, **kwargs)
        assert self.detector_device!=None, "detector device is None"
        
    def set_roi_area(self, area):
        if all([i==0 for i in area]):
            x1,y1,x2,y2=0,0,self.detector_device.size[0]-1,self.detector_device.size[1]-1
        else:
            x1,y1,x2,y2=area
        if x1==x2: x2=x1+1
        if y1==y2: y2=y1+1
        X1=max(min(x1,x2),0)
        X2=min(max(x1,x2),self.detector_device.size[0]-1)
        Y1=max(min(y1,y2),0)
        Y2=min(max(y1,y2),self.detector_device.size[1]-1)
        self.roi_on=True
        return [X1,Y1,X2,Y2]
    
    roi_area=FloatListSetting([0,0,0,0], fixed=False, setter=set_roi_area, numitems=4)
    
    def position(self):
        return float(np.sum(self.detector_device.get_data(self.roi_area)))
    
    def status(self):
        return self.detector_device.call_status()
    
    def do_count(self, tm):
        self.detector_device.lock()
        try:
            self.detector_device.count(tm)
            pos=self.call_position()
            self.detector_device.call_start()
            return pos
        finally:
            self.detector_device.unlock()
            
            