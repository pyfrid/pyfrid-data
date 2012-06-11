import os

import numpy as np

from pyfrid.devices.counters.counter import BaseCounterDevice
from pyfrid.core import use_device

class DummyDetectorDevice(BaseCounterDevice):
    alias="detector"
    channelsnum=24
    
    fpga_device=use_device("fpga")
    
    def start(self, tm=None):
        self.fpga_device.start(tm)

    def stop(self):
        self.fpga_device.stop()

    def read(self):
        Z=np.random.randint(0, 100, size=(self.channelsnum,))
        return Z
    
    def wait(self):
        self.fpga_device.wait()
    
    def clear(self):
        self.fpga_device.clear()
        
    def initialize(self):
        super(DummyDetectorDevice, self).initialize()
        self.call_clear()
        self.call_start()

