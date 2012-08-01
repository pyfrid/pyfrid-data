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
import os
import abc
from threading import Lock

import numpy as np

from pyfrid.core.device import BaseCachedDevice

class BaseDataHandler(object):
    
    def __init__(self, data=None, size=None):
        assert data!=None or size!=None, "data and size are None or empty"
        self._datalock=Lock()
        if data!=None: self._data=np.asarray(data)
        elif size!=None: self._data=np.zeros(size=size)
    
    def get_data(self, area=None):
        pass
    
    def set_data(self, data):
        pass
    
    def sum(self):
        return float(np.sum(self._data))
    
    def max(self):
        return float(np.max(self._data))

    def min(self):
        return float(np.min(self._data))
    
    def save(self, path, base):
        with self._datalock:
            np.savetxt(os.path.join(path, "{0}.gz".format(base)), self._data)
    
    @property        
    def size(self):
        return self._data.shape
        
class DataHandler1D(BaseDataHandler):
    
    def set_data(self, data):
        assert len(data)==len(self._data), "arrays should have the same length"
        with self._datalock:
            self._data[:]=np.asarray(data)
    
    def get_data(self, index=None):
        assert index==None or 0<=index<len(self._data), "index out of range"
        with self._datalock:
            if index==None: return self._data[:]
            return int(self._data[index])
                
class DataHandler2D(BaseDataHandler):
    
    def set_data(self, data):
        assert len(data)==len(self._data), "arrays should have the same length"
        with self._datalock:
            self._data[:,:]=np.asarray(data)
    
    def get_data(self, area=None):
        assert area==None or len(area)==4, "area must be None or an array with four values X1,Y1,X2,Y2"
        with self._datalock:
            if not area: return self._data[:,:]
            x1, y1, x2, y2=min(area[0], area[2]), min(area[1], area[3]),max(area[0], area[2]), max(area[1], area[3]), 
            shape=self._data.shape
            return self._data[shape[1]-y2-1:shape[0]-y1, x1:x2+1]
          
class BaseAbstractCounterDevice(BaseCachedDevice):      
    
    data_handler_class=None
    
    def __init__(self, *args, **kwargs):
        super(BaseAbstractCounterDevice, self).__init__(*args, **kwargs)
        assert issubclass(self.data_handler_class, BaseDataHandler), "Wrong type of the data handler, expecting BaseDataHandler class"
        self._data_handler=self.data_handler_class(self.read())
                               
    def get_data(self, area=None):
        return self._data_handler.get_data(area)
        
    def initialize(self):
        super(BaseAbstractCounterDevice, self).initialize()
        self.call_start()

    def position(self):
        self._data_handler.set_data(self.read())
        return self._data_handler.sum()

    def call_start(self, tm=None):
        if tm: self.info("Starting counting for {0} seconds...".format(tm))
        else: self.info("Starting counting...".format(tm))
        self.call_release()
        self.start(tm)
        self.force_update()
        
    def call_clear(self):
        self.info("Clearing...")
        self.clear()
        self.force_update()
        
    def call_wait(self):
        self.info("Waiting...")
        self.wait()
        self.force_update()
    
    def call_save(self, path, base):
        self.info("Saving data...")
        self.force_update()
        self._data_handler.save(path, base)
        
    @abc.abstractmethod                                              
    def start(self,tm=None):
        pass
    
    @abc.abstractmethod
    def stop(self):
        pass
    
    @abc.abstractmethod
    def clear(self):
        pass
    
    @abc.abstractmethod
    def wait(self):
        pass
            
    @abc.abstractmethod        
    def read(self):
        pass
    
    def count(self, tm):
        self.call_stop()
        self.call_clear()
        self.call_start(tm)
        self.call_wait()
        self.call_stop()
        self.force_update()
        
    def do_count(self,tm):
        self.count(tm)
        pos=self.call_position()
        self.call_start()
        return pos
    
    