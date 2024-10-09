import pandas as pd
import numpy as np
import xarray as xr
import re
import os
from pathlib import Path
import bp12_tools.model_utils as mu
#
# Contains functions for reading data from chpc cluster
# Option "is_sorted" returns data on a cleaned lat lon gris
# else returns on original model grid
#

def get_bp12filenames(ftype, filedates):
    '''
    for use on cluster, returns 2 lists:
    list 1. full path to each file for the required dates
    list 2. pandas timestamps to overwrite model dates
    '''
    indir = '/mnt/nrestore/users/ERTH0834/BIOPERIANT12/BIOPERIANT12-CNCLNG01-S'
    dates_alph = re.sub('[0-9]', '', filedates)
    dates_nums = re.sub(r'[^0-9]', '', filedates)
    if dates_alph == 'y':
        yr = int(filedates.split('y')[1])
        dates_model =  mu.get_mmdd_5d(yr)
    elif (not dates_alph) and (1988 < int(dates_nums) < 2010):
        yr = int(dates_nums)
        dates_model =  mu.get_mmdd_5d(yr)
    elif dates_alph =='ym':
        yr, mm = int(dates_nums[:4]), int(dates_nums[4:6])
        dates_model = [datestr for datestr in mu.get_mmdd_5d(yr) if f"m{mm:02d}"in datestr]
    elif dates_alph =='ymd':
        yr = int(dates_nums[:4])
        dates_model = [filedates]

    filenames, ts = [], []
    for dd in dates_model:
        filename = f"{indir}/{yr}/BIOPERIANT12-CNCLNG01_{dd}_{ftype}.nc"
        if os.path.isfile(filename):
            filenames.append(filename)  
            ts.append(pd.Timestamp(int(dd[1:5]), int(dd[6:8]), int(dd[9:11]) ,12))
    return filenames, ts

def get_bp12var(varname, vardates, zlev):
    '''
    returns variable on sorted grid with correct timestamps
    if zlev < 0 will return whole water column
    '''
    ftype = get_filetype(varname)
    if not ftype: 
        return None

    filenames, ts = get_bp12filenames(ftype, vardates)
    ds = xr.open_mfdataset(filenames, decode_times=False, 
                           chunks={'y': 561, 'x': 1080},
                           concat_dim='time_counter', combine='nested')
    ds['time_counter'] = ts[:]  
    
    # read variable
    if varname in ['pp','PP']: 
        var = ds['PPPHY'] + ds['PPPHY2']
    elif varname in ['chl','CHL']: 
        var = ds['NCHL'] + ds['DCHL']
    else:       
        var = ds[varname]
        
    if 'depthu' in var.dims:
        var = var.rename({'depthu':'deptht'})
    if 'depthv' in var.dims:
        var = var.rename({'depthv':'deptht'})
    if 'depthw' in var.dims:
        var = var.rename({'depthw':'deptht'})
        
    # now sort
    var = var.rename({'y':'lat', 'x':'lon','time_counter':'time'})
    var = var.assign_coords(lat=("lat", ds.nav_lat[0,:,0].values), 
                            lon=("lon", ds.nav_lon[0,0,:].values))
    var = var.sortby('lon').drop_duplicates('lon', keep='first') 
    
    # Prep clean dataset for return
    if (zlev >= 0) or (var.ndim == 3):
        if var.ndim > 3: var = var.isel(deptht=zlev)  
        var = var.chunk(chunks={"time":var.time.size, "lat":561, "lon":1080})
        return var
    else:
        var = var.chunk(chunks={"time":var.time.size, 
                                "deptht":var.deptht.size, "lat":561,"lon":1080})
        return var
    
def get_bp12var_subset(varname, vardates, zlev, yxinds):
    '''
    returns subset of variable on sorted grid with correct timestamps
    '''
    j1, j2, i1, i2 = yxinds
    varout = get_bp12var(varname, vardates, zlev)
    return varout.isel(lat=slice(j1,j2), lon=slice(i1,i2))
    

def get_bp12input(varname, filename, is_sorted=1):
    ''' 
    returns variable from any model file
    with grid sorted
    '''
    ds_in = xr.open_dataset(filename, decode_times= False) 
    var = ds_in[varname]
    
    if is_sorted == 1:
        if "z" in var.dims: var = var.rename({'z':'deptht'})
        if "x" in var.dims:
            ds_in = ds_in.rename({'x':'lon', 'y':'lat'})
            ds_in = ds_in.assign_coords( lat=("lat", ds_in.nav_lat[:,0].values), 
                                     lon=("lon", ds_in.nav_lon[0,:].values ))
            var = ds_in[varname].sortby('lon').drop_duplicates('lon', keep='first')
       
    return var