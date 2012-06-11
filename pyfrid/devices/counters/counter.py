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

from pyfrid.core import BaseDevice
from pyfrid.devices.counters.core.counter import BaseAbstractCounterDevice, DataHandler1D

class BaseCounterDevice(BaseAbstractCounterDevice):
    data_handler_class=DataHandler1D
    
    
class BaseMonitorDevice(BaseDevice):
    index=0
    counter_device=None
    
    def __init__(self, *args, **kwargs):
        super(BaseMonitorDevice, self).__init__(*args, **kwargs)
        assert self.counter_device!=None, "counter device is None"
    
    def position(self):
        return self.counter_device.get_data(self.index)
    
    def status(self):
        return self.counter_device.call_status()
    
    def do_count(self, tm):
        self.counter_device.lock()
        try:
            self.counter_device.count(tm)
            pos=self.call_position()
            self.counter_device.call_start()
            return pos
        finally:
            self.counter_device.unlock()
    