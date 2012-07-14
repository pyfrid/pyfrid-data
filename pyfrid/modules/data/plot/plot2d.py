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

from threading import Lock
import numpy as np

from pyfrid.modules.data.core.handler import BaseDataHandlerModule
from pyfrid.modules.plot.plot2d import BasePlot2DModule

class BasePlot2DDataModule(BaseDataHandlerModule, BasePlot2DModule):
    
    def_xdev=None
    def_ydev=None
    
    def __init__(self, *args, **kwargs):
        super(BasePlot2DDataModule, self).__init__(*args, **kwargs)
        assert self.def_xdev!=None, "default x axis device is None"
        assert self.def_ydev!=None, "default y axis device is None"
        self._axislock=Lock()
        self._xdata=None
        self._xdev=None
        self._ydev=None
        self.set_xdev(self.def_xdev)
        self.set_ydev(self.def_ydev)
    
    def xticks_formatter(self, val, pos=None):
        try:
            return "{0:.4f}".format(self._xdata[int(val)])
        except IndexError: # very bad, must be redone
            return "{0:.4f}".format(self._xdata[-1])
    
    def init_data(self, *args, **kwargs):
        self.init_plot()
    
    def dump_data(self, *args, **kwargs):
        self.update_plot()
                        
    def close_data(self,**kwargs):
        pass

    def get_data(self, area=None):
        with self._axislock:
            xdata=np.asarray(self.data_module.get_data(self._xdev.name))
            ydata=np.asarray(self.data_module.get_data(self._ydev.name))
            if len(ydata)==0: 
                xdata=np.asarray([0])
                ydata=np.asarray([0])
        self._xdata=xdata
        return ydata
        
    def set_xdev(self, dev, update=False):
        with self._axislock:
            self._xdev=dev
            self.xlabel="{0}[{1}]".format(dev.name, dev.units)
        if update: self.update_plot()
    
    def set_ydev(self, dev, update=False):
        with self._axislock:
            self._ydev=dev
            self.ylabel="{0}[{1}]".format(dev.name, dev.units)
        if update: self.update_plot()
        
    