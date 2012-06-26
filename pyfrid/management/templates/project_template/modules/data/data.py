#    This file is part of PyFRID.
#
#    PyFRID is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFRID is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFRID.  If not, see <http://www.gnu.org/licenses/>.
#

from pyfrid.core import use_device, BoolSetting
from pyfrid.modules.data.core.data import BaseDataModule

class DataModule(BaseDataModule):
    alias="data"
    
    fpga_device=use_device("dummy_fpga")
    shutter_device=use_device("dummy_shutter")
    noshutter=BoolSetting(False, fixed=False)
    
    def shoot(self, tm):
        if not self.noshutter:
            pos=self.shutter_device.call_position()
            if not pos and not self.shutter_device.do_switch(True):
                self.error("Can not open shutter")
                self.call_stop()
            else: self.fpga_device.count(tm)        
            
    
