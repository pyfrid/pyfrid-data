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
#

import cStringIO
import uuid
import base64
import abc
from threading import Lock

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas 

from pyfrid.core.module import BaseModule

from pyfrid.core.settings import IntListSetting, IntSetting

COLORS=["blue", "green", "red", "cyan", "magenta", "yellow", "black", "white"]


class BasePlotModule(BaseModule):
    
    figsize=IntListSetting([6,6], fixed=True, numitems=2)
    dpi=IntSetting(60, fixed=True, limits=[10, 200])
    
    def __init__(self, *args, **kwargs):
        super(BasePlotModule, self).__init__(*args, **kwargs)
        
        self._fig=Figure(self.figsize,self.dpi)
        self._canvas=FigureCanvas(self._fig)
        
        self._data=None
        self._cache=""
        
        self._id=''
        self._enabled=False
        
        self._zoom=[]
        self._masks=[]
        
        self._lockfig    =  Lock()
        self._lockcache  =  Lock()
        self._lockdata   =  Lock()
        self._lockzoom   =  Lock()
    
    @abc.abstractmethod
    def calc_coord(self,x,y):
        return 0.0,0.0

    @abc.abstractmethod
    def init_components(self):
        pass
    
    @abc.abstractmethod
    def update_components(self):
        pass
    
    @abc.abstractmethod
    def get_data(self, area=None):
        pass

    def init_plot(self):
        with self._lockfig:
            try:
                self.clear_figure()
                with self._lockdata:
                    data=np.asarray(self.get_data())
                    self._data=np.ma.array(data=data, mask=np.zeros(data.shape, dtype=np.bool))
                self.init_components()
            except Exception, err:
                self.exception("Exception while initializing plot components: {0}".format(err))
    
    def update_plot(self):
        with self._lockfig:
            if self._enabled:
                try:
                    with self._lockdata:
                        d=self.get_data(self.zoom_area)
                        if len(self._data)!=len(d):
                            self._data=np.ma.resize(self._data, len(d))
                        self._data.data[:]=np.asarray(d)
                    self.update_components()
                    self._update_cache()
                except Exception, err:
                    self.exception("Exception while updating plot components: {0}".format(err))
            
    def set_zoom(self, x1, y1, x2, y2):
        with self._lockzoom:
            if self._enabled:
                self._zoom=[min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)]
                self.update_plot()
    
    def clear_zoom(self):
        with self._lockzoom:
            if self._enabled:
                self._zoom=[]
                self.update_plot()
    
    @property
    def zoom_area(self):
        return self._zoom[:]
    
    @property
    def enabled(self):
        return self._enabled
    
    @enabled.setter
    def enabled(self,val):
        self._enabled=bool(val)
        if self._enabled: 
            self.update_plot()
    
    def resize(self,w,h):
        with self._lockfig:
            try:
                w=w/float(self._fig.dpi)
                h=h/float(self._fig.dpi)
                self._fig.set_size_inches(w,h)
                self._update_cache()
            except Exception, err:
                self.warning("Exception: {0}".format(err))
            return self.get_image(0)
    
    def _update_cache(self):
        with self._lockcache:
            if self._enabled:
                fh=cStringIO.StringIO()
                try:
                    self._fig.savefig(fh,format='png')
                    fh.seek(0)
                    self._cache=fh.getvalue()
                    self._id=str(uuid.uuid4())
                except Exception, err:
                    self.warning("Warning: {0}".format(err))
                finally:
                    fh.close()
                
    def get_image(self, id):
        with self._lockcache:
            if self._id!=id and self._enabled:
                return {
                    "id":self._id,
                    "image":base64.encodestring(self._cache)
                }
            return None
        
    def get_coordinates(self,x,y):
        with self._lockfig:
            if self._enabled:
                xd,yd=self.calc_coord(x,y)
                return [xd,yd]
            return 0.0, 0.0
    
    def iterate_masks(self):
        for mask in self._masks:
            yield mask[:]
            
    def initialize(self):
        self.init_plot()
        
    def set_settings(self,settings=[]):
        with self._lockfig:
            objsetlist=self.settings(permission=["set","get"])
            for s in settings:
                sn=s["name"]
                if sn in objsetlist:
                    setattr(self,sn,s["value"])
        self.update_plot()
                    
    def get_settings(self):
        output=[]
        for setname, setobj in self.iterate_settings(permission=["set","get"]):
            output.append((setname,getattr(self,setname),setobj.units,setobj.docs, setobj.expected, setobj.typename))
        return output

    def clear_figure(self):
        self._fig.clear()
    