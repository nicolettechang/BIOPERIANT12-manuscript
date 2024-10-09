import pandas as pd
import numpy as np
from math import pi
import xarray as xr
from scipy import stats
# trend analysis
import pymannkendall as mk
import statsmodels.api as sm
from io import StringIO
import contextlib

################################################### 
#
# Math and statistics functions
# 
################################################### 
def pceil(a, precision=0):
    ''' 
    round up a float (a) to specific number of decimal places (precision)
    '''
    return np.true_divide(np.ceil(a * 10**precision), 10**precision)

def pfloor(a, precision=0):
    ''' 
    round down a float (a) to specific number of decimal places (precision)
    '''
    return np.true_divide(np.floor(a * 10**precision), 10**precision)


def get_pdf(var_in, perc_outlier=None):
    '''
    Takes in an array and caculates the upper and lower bound
    Returns sorted variable an the generated pdf
    If perc_outlier, also return the lower and upper percentage of gridpoints 
    that are outliers.
    '''
    # remove outliers
    var_in = var_in.stack(ll=('lat','lon')).sortby('ll')
    Q1, Q3 = np.nanpercentile(var_in, 25), np.nanpercentile(var_in, 75)
    IQR = Q3 - Q1
    upper, lower = Q3+1.5*IQR, Q1-1.5*IQR
    ngpts_mdl = var_in.lat.size * var_in.lon.size
    upper_array, lower_array = np.array(var_in>=upper), np.array(var_in<=lower)
   
    var_in = var_in.where(lower<var_in, np.nan) 
    var_in = var_in.where(var_in<upper, np.nan)     
    var_sort = np.sort(var_in.values)
    pdf_var = stats.norm.pdf(var_sort, loc=np.nanmean(var_sort), scale=np.nanstd(var_sort))
    if perc_outlier:        
        uop, lop = upper_array.sum()/ngpts_mdl*100, lower_array.sum()/ngpts_mdl*100
        print(f"Upper Bound = {upper:3.3f}, percent outliers= {uop:2.4f}")
        print(f"Lower Bound = {lower:3.3f}, percent outliers= {lop:2.4f}")
        return var_sort, pdf_var, (lop, uop)
    else:
        return var_sort, pdf_var


def get_trend(da_in):
    '''
    Get trend in a timeseries with dimension time or time_counter
    '''
    if not 'time' in da_in.dims:
        da_in = da_in.rename({'time_counter':'time'})        
    p = da_in.polyfit(dim="time", deg=1)
    trend = xr.polyval(da_in.time, p.polyfit_coefficients)
    return trend

def check_trend(da_in, testnum=0):
    '''
    Check significance of trend in a timeseries
    default option is Original Mann-Kendall Test
    '''
    f = StringIO()
    with contextlib.redirect_stdout(f):
        # Original MK
        if testnum ==0: 
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.original_test(da_in, alpha=0.05)
        # MK tests for data with autocorrelation
        if testnum ==1:
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.hamed_rao_modification_test(da_in, alpha=0.05)
        if testnum ==2: 
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.yue_wang_modification_test(da_in, alpha=0.05)
        if testnum ==3:
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.trend_free_pre_whitening_modification_test(da_in, alpha=0.05)
        if testnum ==4:
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.pre_whitening_modification_test(da_in, alpha=0.05)
        if testnum ==5:
            trend, h, p, z, Tau, s, var_s, slope, intercept = mk.seasonal_test(da_in, alpha=0.05)
        return trend, p
