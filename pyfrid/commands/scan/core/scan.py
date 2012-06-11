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

from pyfrid.core import BaseCommand

class BaseScanCommand(BaseCommand):
    
    data_module=None
    
    def __init__(self, *args, **kwargs):
        super(BaseScanCommand,self).__init__(*args, **kwargs)
        assert self.data_module!=None, "data module is None"
        self.data_module.after_stop_signal.connect(self.on_datamod_stop)
        
    def on_datamod_stop(self, *args, **kwargs):
        self.call_stop()
    
    def validate_data(self, *args,**kwargs):
        return self.data_module.validate_data()
    
    def acquire_data(self, tm, *args,**kwargs):
        return self.data_module.acquire_data(tm, *args,**kwargs)
    
    def init_data(self, *args, **kwargs):
        return self.data_module.init_data(*args,**kwargs)
    
    def close_data(self, *args, **kwargs):
        return self.data_module.close_data(*args,**kwargs)