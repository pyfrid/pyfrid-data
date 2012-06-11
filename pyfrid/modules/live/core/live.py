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

import time
from threading import Thread
from pyfrid.core.settings import FloatSetting
from pyfrid.core.module import BaseModule

class BaseLiveDisplayModule(BaseModule):
    poll_pause=FloatSetting(1.0)
    detector_device=None
    
    def __init__(self, *args, **kwargs):
        super(BaseLiveDisplayModule, self).__init__(*args, **kwargs)
        assert self.detector_device!=None, "detector device is None"
        self._poller=Thread(target=self._poll)
        self._poller.setDaemon(True)
        self._stop_poll=False
        self._data=[]
                    
    def _poll(self):
        while not self._stop_poll:
            if not self.has_exception:
                self.update_plot()
            time.sleep(self.poll_pause)    
            
    def call_shutdown(self):
        self._stop_poll=True
        self._poller.join()
        super(BaseLiveDisplayModule,self).call_shutdown()
       
    def call_initialize(self):
        super(BaseLiveDisplayModule,self).call_initialize()
        if not self._poller.is_alive():
            self._poller.start()
            
        