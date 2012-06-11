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

import abc
import numpy as np

import matplotlib.gridspec as gridspec
from matplotlib.cm import get_cmap, datad 
from matplotlib.colors import LogNorm, Normalize
from matplotlib.ticker import LogLocator, LogFormatter
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import MaxNLocator

from matplotlib.patches import Rectangle

from pyfrid.modules.plot.core.plot import BasePlotModule, COLORS

from pyfrid.core.settings import BoolSetting, FloatListSetting, StringSetting

COLORMAPS=sorted(m for m in datad if not m.endswith("_r"))

   
class BaseMapModule(BasePlotModule):
    
    cblog=BoolSetting  ( False, fixed=False )
    cbrange=FloatListSetting([None,None], fixed=False, numitems=2, allownone=True)
    
    cbmap=StringSetting("jet", fixed=False, expected=COLORMAPS)
    
    mask_color=StringSetting("red", expected=COLORS)
    lines_color=StringSetting("black", expected=COLORS)
    
    def __init__(self, *args, **kwargs):
        super(BaseMapModule, self).__init__(*args, **kwargs)
        self._center=(0,0)
        self._mask_rects=[]
        self._lines=[]        
    
    def init_plot(self):
        super(BaseMapModule,self).init_plot()
        self.reset_center()
    
    def init_components(self):
        gs = gridspec.GridSpec(3, 2, width_ratios=[4,1], height_ratios=[1,4,0.2], hspace=0.35)
        self._axmap  = self._fig.add_subplot(gs[2])
        self._axintx = self._fig.add_subplot(gs[0])
        self._axinty = self._fig.add_subplot(gs[3])
        self._axcb   = self._fig.add_subplot(gs[4])
        
        data=self.get_data()
        data_xint=np.sum(data,0)
        data_yint=np.flipud(np.sum(data,1))
        
        self._image=self._axmap.imshow(data, aspect="auto", interpolation="nearest", clip_on=True)
        self._cb=self._fig.colorbar(self._image, cax=self._axcb, orientation='horizontal')
                
        self._plotx=self._axintx.plot(np.arange(0,len(data_xint)),data_xint)[0]
        self._ploty=self._axinty.plot(data_yint,np.arange(0,len(data_xint)))[0]
        
        self._axintx.axes.get_xaxis().set_visible(False)
        self._axinty.axes.get_yaxis().set_visible(False)
        
        self._axmap.yaxis.set_major_locator(MaxNLocator(4))
        self._axmap.xaxis.set_major_locator(MaxNLocator(4))
        
    def update_components(self):
        data=self._data
        if self._zoom:
            x1, y1, x2, y2=self.zoom_area
            data=np.ma.array(data=data.data[data.shape[1]-y2-1:data.shape[0]-y1,x1:x2+1],
                             mask=data.mask[data.shape[1]-y2-1:data.shape[0]-y1,x1:x2+1])
        data_max=np.max(data)
        data_min=np.min(data)
        if self.cblog and data_max==0.0: return 
        ylen=data.shape[0]
        xlen=data.shape[1]
        data_xint=np.sum(data,0)
        data_yint=np.flipud(np.sum(data,1))
        dxmax=np.max(data_xint)
        dymax=np.max(data_yint)
        cbmin,cbmax=self.cbrange
        self._image.set_data(data)
        self._plotx.set_ydata(data_xint)
        self._plotx.set_xdata(np.arange(0,xlen))
        self._ploty.set_xdata(data_yint)
        self._ploty.set_ydata(np.arange(0,ylen))
        if self.cblog:  
            cbmin=max(data_min, 1e-5) if cbmin==None else max(cbmin, 1e-5)
            cbmax=data_max if cbmax==None else max(cbmax,1e-5)
            self._axintx.set_yscale('symlog', basey=10, subsy=None, nonposy="mask")
            self._axinty.set_xscale('symlog', basex=10, subsx=None, nonposx="mask")
            self._image.set_norm(LogNorm(cbmin,cbmax,clip=True))
            self._cb.set_norm(LogNorm(cbmin,cbmax,clip=True))
            self._cb.set_ticks(LogLocator(1000))
            self._cb.ax.xaxis.set_major_formatter(LogFormatter())
            self._axintx.yaxis.set_major_locator(LogLocator(1000))
            self._axinty.xaxis.set_major_locator(LogLocator(1000))
        else:
            cbmin=data_min if cbmin==None else cbmin
            cbmax=data_max if cbmax==None else cbmax
            self._axintx.set_yscale('linear')
            self._axinty.set_xscale('linear')
            self._image.set_norm(Normalize(cbmin,cbmax,clip=True))
            self._cb.set_norm(Normalize(cbmin,cbmax,clip=True))
            self._cb.set_ticks(MaxNLocator(3))
            self._cb.ax.xaxis.set_major_formatter(ScalarFormatter())
            self._axintx.yaxis.set_major_locator(MaxNLocator(2))
            self._axinty.xaxis.set_major_locator(MaxNLocator(2))
        self._axintx.set_ylim(0,dxmax)
        self._axinty.set_xlim(0,dymax) 
        
        cbmap=get_cmap(self.cbmap)
        self._image.set_cmap(cbmap)
        self._cb.set_cmap(cbmap)
        
        self.draw_lines(xlen, ylen)
        
        zoom=self.zoom_area
        if zoom:
            self._image.set_extent([zoom[0],zoom[2],zoom[1],zoom[3]])
        else:
            self._image.set_extent([0,xlen,0,ylen])
        self._axintx.set_xlim(0,xlen)
        self._axinty.set_ylim(0,ylen)    
        self._image.set_clim(cbmin, cbmax)    
        self._cb.update_normal(self._image)
        
        self.draw_masks()
            
    def calc_coord(self,x,y):
        inv = self._axmap.transData.inverted()
        xd,yd=inv.transform_point((x, y))
        return [float(xd), float(yd)]
     
    @abc.abstractmethod
    def get_data(self, area=None):
        pass
            
    def set_center(self,x,y):
        self._center=(x,y)
        
    def reset_center(self):
        self._center=(self._data.shape[1]//2.0,self._data.shape[0]//2.0)
    
    @property
    def center(self):
        return self._center
                            
    def add_mask(self,x1,y1,x2,y2):
        with self._lockdata:
            if x1==x2: x2=x1+1
            if y1==y2: y2=y1+1
            shape=self._data.shape
            X1=int(max(min(x1,x2),0))
            X2=int(min(max(x1,x2),shape[1]-1))
            Y1=int(max(min(y1,y2),0))
            Y2=int(min(max(y1,y2),shape[0]-1))
            try:
                self._masks.append([X1,Y1,X2,Y2])
                self._data.mask[shape[1]-Y2-1:shape[0]-Y1,X1:X2+1]=np.ones((Y2-Y1+1,X2-X1+1))
            except:
                self.exception("Exception while adding mask")
        self.update_plot()
    
    def clear_mask(self):
        with self._lockdata:
            try:
                shape=self._data.shape
                self._data.mask=np.zeros(shape)
                self._masks=[]
            except:
                self.exception("Exception while clearing masks")
        self.update_plot()
            
    def clear_last_mask(self):
        with self._lockdata:
            try:
                shape=self._data.shape
                if self._masks:
                    X1,Y1,X2,Y2=self._masks[-1]
                    self._data.mask[shape[1]-Y2-1:shape[0]-Y1,X1:X2+1]=np.zeros((Y2-Y1+1,X2-X1+1))
                    del self._masks[-1]
            except:
                self.exception("Exception while deleting masks")
        self.update_plot()
        
    def draw_masks(self):
        try:
            map(lambda m: m.remove(), self._mask_rects)
        except:
            pass
        self._mask_rects=[]
        for mask in self.iterate_masks():
            h=mask[3]-mask[1]+1
            w=mask[2]-mask[0]+1
            x0=mask[0]
            y0=mask[1]
            rect=Rectangle((x0,y0),w,h,fill=True,color=self.mask_color)
            self._axmap.add_patch(rect)
            self._mask_rects.append(rect)
            
    def draw_lines(self, xlen, ylen):
        (xc,yc)=self._center
        map(lambda l: l.remove(), self._lines)
        self._lines=[]
        
        self._lines.append(self._axmap.axhline  (y=(yc), linewidth=1.4, color=self.lines_color))
        self._lines.append(self._axmap.axvline  (x=(xc), linewidth=1.4, color=self.lines_color))
        
        self._lines.append(self._axinty.axhline (y=(yc), linewidth=1.4, color=self.lines_color))
        self._lines.append(self._axintx.axvline (x=(xc), linewidth=1.4, color=self.lines_color))
