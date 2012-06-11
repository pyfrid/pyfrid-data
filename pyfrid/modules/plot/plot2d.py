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

import numpy as np

from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

from pyfrid.modules.plot.core.plot import BasePlotModule, COLORS

from pyfrid.core import BoolSetting, StringSetting

class BasePlot2DModule(BasePlotModule):
    
    xlabel= StringSetting  ("X", fixed=True)
    ylabel= StringSetting  ("Y", fixed=True)
    
    xaxis_log=BoolSetting  ( False, fixed=False )
    yaxis_log=BoolSetting  ( False,  fixed=False )
    
    mask_color=StringSetting("red",  expected=COLORS)
    
    def __init__(self, *args, **kwargs):
        super(BasePlot2DModule, self).__init__(*args, **kwargs)
        self._mask_rects=[]
        
    def init_components(self):
        self._axis=self._fig.add_subplot("111")
        self._line1=self._axis.plot([0.0],[0.0],"o-")[0]
    
    def set_formatters(self):
        try: func=getattr(self, "xticks_formatter")
        except AttributeError: pass
        else: self._axis.xaxis.set_major_formatter(FuncFormatter(func))
        try: func=getattr(self, "yticks_formatter")
        except AttributeError: pass
        else: self._axis.yaxis.set_major_formatter(FuncFormatter(func))
               
    def update_components(self,**kwargs):
        datay=self._data
        datax=np.asarray(range(len(datay)))
        
        self._line1.set_ydata(datay)
        self._line1.set_xdata(datax)
        
        zoom=self.zoom_area
        if zoom:
            xmin,ymin,xmax,ymax=zoom
            self._axis.set_ylim(ymin,ymax)
            self._axis.set_xlim(xmin,xmax)
        else:
            self._axis.set_ylim(np.ma.min(datay),np.ma.max(datay))
            self._axis.set_xlim(np.ma.min(datax),np.ma.max(datax))
        if self.xaxis_log:
            self._axis.set_xscale('symlog', basex=10, subsx=None, nonposx="mask")  
        else:
            self._axis.set_xscale('linear')    
        if self.yaxis_log:
            self._axis.set_yscale('symlog', basey=10, subsy=None, nonposy="mask")
        else:
            self._axis.set_yscale('linear')
        
        self.set_formatters()    
        self._axis.set_xlabel(self.xlabel)
        self._axis.set_ylabel(self.ylabel)
        
        self.draw_masks()
                
    def calc_coord(self,x,y):
        inv = self._axis.transData.inverted()
        xd,yd=inv.transform_point((x, y))
        return [float(xd), float(yd)]
    
    def add_mask(self,x1, y1, x2, y2):
        with self._lockdata:
            if x1==x2: x2=x1+1
            X1=min(int(x1),int(x2))
            X2=max(int(x1),int(x2))
            Y1=min(y1,y2)
            Y2=max(y1,y2)
            try:
                self._masks.append([X1, Y1, X2, Y2])
                self._data.mask[X1:X2+1]=np.ones((X2-X1+1,))
            except:
                self.exception("Exception while adding mask")
        self.update_plot()
    
    def clear_mask(self):
        with self._lockdata:
            try:
                self._data.mask=np.zeros(self._data.shape)
                self._masks=[]
            except:
                self.exception("Exception while clearing masks")
        self.update_plot()

    def clear_last_mask(self):
        with self._lockdata:
            try:
                if self._masks:
                    X1,_,X2,_=self._masks[-1]
                    self._data.mask[X1:X2+1]=np.zeros((X2-X1+1,))
                    del self._masks[-1]
            except:
                self.exception("Exception while deleting masks")
        self.update_plot()
            
    def draw_masks(self):
        map(lambda m: m.remove(), self._mask_rects)
        self._mask_rects=[]
        for mask in self.iterate_masks():
            lim=self._axis.get_ylim()
            h=lim[1]-lim[0]
            w=mask[2]-mask[0]+1
            x0=mask[0]
            y0=mask[1]
            rect=Rectangle((x0,lim[0]),w,h,fill=True,color=self.mask_color)
            self._axis.add_patch(rect)
            self._mask_rects.append(rect)
            
    def clear_figure(self):
        super(BasePlot2DModule, self).clear_figure()
        self._mask_rects=[]
            
