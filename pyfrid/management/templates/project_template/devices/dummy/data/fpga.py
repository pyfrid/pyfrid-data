import time
import numpy as np

from pyfrid.devices.counters.counter import BaseCounterDevice, BaseMonitorDevice
from pyfrid.core import use_device, BaseDevice

class DummyFpgaDevice(BaseCounterDevice):
    alias="dummy_fpga"
    channelsnum=2
    
    def __init__(self, *args, **kwargs):
        super(DummyFpgaDevice, self).__init__(*args, **kwargs)
        self._start=None
        self._time=None

    def get_time(self):
        if self._start==None: return 0.0
        return time.time()-self._start
    
    def start(self, tm=None):
        self._time=tm
        self._start=time.time()

    def stop(self):
        pass

    def read(self):
        return np.random.randint(0, 100, size=(self.channelsnum,))
    
    def wait(self):
        if self._start==None:
            self.error("FPGA has not being started yet.")
        if self._time!=None:
            while time.time()-self._start<self._time and not self.stopped: time.sleep(0.02)
    
    def clear(self):
        self._time=None
        self._start=None
        
    def initialize(self):
        super(DummyFpgaDevice, self).initialize()
        self.call_clear()
        self.call_start()

    
class TimeDevice(BaseDevice):
    alias="fpga_time"
    counter_device=use_device("dummy_fpga")
    
    def position(self):
        return self.counter_device.get_time()

    
class Monitor1Device(BaseMonitorDevice):
    alias="fpga_monitor1"
    index=0
    counter_device=use_device("dummy_fpga")


class Monitor2Device(BaseMonitorDevice):
    alias="fpga_monitor2"
    index=1
    counter_device=use_device("dummy_fpga")


