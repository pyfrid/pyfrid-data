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

from pyfrid.core import use_device
from pyfrid.modules.live.map import BaseLiveMapModule
from pyfrid.webapp.modules.live.map import LiveMapModuleWebRouter

class LiveMapModule(BaseLiveMapModule):
    alias="map"
    webrouter=LiveMapModuleWebRouter
    webscript="modules/live/map.js"
    webbases=[
              "project_static/js/core/data/baseplot.js",
              "project_static/js/core/data/mapplot.js"
             ]
    
    detector_device=use_device("psd")