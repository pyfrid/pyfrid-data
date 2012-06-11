
import numpy as np
from pyfrid.core import use_device
from pyfrid.devices.counters.psd import BasePSDDevice

class DummyPSDDevice(BasePSDDevice):
    alias="psd"
    
    fpga_device=use_device("fpga")
            
    def start(self, tm=None):
        self.fpga_device.start(tm)

    def stop(self):
        self.fpga_device.stop()
    
    def wait(self):
        self.fpga_device.wait()
    
    def clear(self):
        self.fpga_device.clear()
    
    def read(self):
        X,Y=np.mgrid[-5:5:0.05,-5:5:0.05]
        Z=np.sqrt(X**2+Y**2)+np.sin(X**2+Y**2)
        return Z
            