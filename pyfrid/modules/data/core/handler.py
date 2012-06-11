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

import abc
import time
from pyfrid.core import BaseModule

class BaseDataHandlerModule(BaseModule):
    
    data_module=None
    
    def __init__(self,*args,**kwargs):
        super(BaseDataHandlerModule,self).__init__( *args, **kwargs )
        assert self.data_module!=None, "data module is None"
        self.data_module.register_handler(self)
    
    @abc.abstractmethod    
    def init_data(self, *args, **kwargs):
        pass
    
    @abc.abstractmethod
    def dump_data(self, *args, **kwargs):
        pass
    
    @abc.abstractmethod        
    def close_data(self,**kwargs):
        pass
    
    