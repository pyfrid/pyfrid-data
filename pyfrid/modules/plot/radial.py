import numpy as np

from pyfrid.modules.plot.plot2d import BasePlot2DModule
from pyfrid.modules.live.core.live import BaseLiveDisplayModule

class BaseRadialModule(BasePlot2DModule):
    
    map_module=None
    
    def __init__(self, *args, **kwargs):
        super(BaseRadialModule, self).__init__(*args, **kwargs)
        self.xlabel="radius"
        self.ylabel="Average"
    
    def get_data(self, area=None):
        return np.asarray(self.detector_device.get_data())
    
    def call_shutdown(self):
        super(BaseRadialModule, self).call_shutdown()
       
    def call_initialize(self):
        super(BaseRadialModule, self).call_initialize()
        
    def radial_average(self, image, center=None, binsize=1.0):
        """
        Calculate the azimuthally averaged radial profile.
    
        image - The 2D image
        center - The [x,y] pixel coordinates used as the center. The default is 
                 None, which then uses the center of the image (including 
                 fractional pixels).
        stddev - if specified, return the azimuthal standard deviation instead of the average
        returnradii - if specified, return (radii_array,radial_profile)
        return_nr   - if specified, return number of pixels per radius *and* radius
        binsize - size of the averaging bin.  Can lead to strange results if
            non-binsize factors are used to specify the center and the binsize is
            too large
        
        Taken from http://www.astrobetter.com/wiki/tiki-index.php?page=python_radial_profiles
        via Jessica R. Lu
        """
        # Calculate the indices from the image
        y, x = np.indices(image.shape)
    
        if center is None:
            center = np.array([(x.max()-x.min())/2.0, (y.max()-y.min())/2.0])
        
        #creating a 2d matrix of all radii
        r = np.hypot(x - center[0],y - center[1])
        #print "radii", r
        # Get sorted radii indices
        ind = np.argsort(r.flat)
        #1d array of sorted indecies of radii
        i_sorted = image.flat[ind]  # sorted image
        i_sorted_zeros=np.ma.filled(i_sorted,0)
        #print "sorted image", i_sorted
        r_sorted = np.array(r.flat[ind])      # sorted radii
        #print "sorted radii", r_sorted
    
        # Get the integer part of the radii (bin size = 1)
        r_binned = np.round(r_sorted/binsize)*binsize
        #print "sorted binned radii", r_binned
        # Find all pixels that fall within each radial bin.
        deltar = r_binned[1:] - r_binned[:-1]  # Assumes all radii represented
        deltar[-1] = binsize                   # include outermost points
        #print "deltar", deltar
        rind = np.concatenate(([0],np.where(deltar)[0]+1))   # location of changed radius (minimum 1 point)
        #print "nonzero delta indices", rind
        index_cs = np.ma.cumsum(np.ma.masked_array(np.ones(len(i_sorted),dtype=np.int),mask=i_sorted.mask)).data
        nr = index_cs[rind[1:]] - index_cs[rind[:-1]] # include innermost bin
        nr[-1]+=1
        # Cumulative sum to figure out sums for each radius bin
        #print "number of radii", nr
            # Cumulative sum to figure out sums for each radius bin
        csim = np.ma.cumsum(i_sorted, dtype=float).data
        #print "cumsum", csim
        tbin = csim[rind[1:]] - csim[rind[:-1]] # include innermost bin
        if len(rind)>1: tbin[-1]+=i_sorted_zeros[rind[-2]]
        #print "tbin", tbin
        profile=np.nan_to_num(tbin/nr)
        #print "profile", r_binned[rind[:-1]],profile
        return  (r_binned[rind[:-1]], profile)