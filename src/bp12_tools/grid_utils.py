import numpy as np
from math import pi
import xarray as xr

################################################### 
#
# Contains functions used for grid averging,
# size/weighting
# 
################################################### 

def get_bp12grid(varname, is_sorted=1):
    ''' 
    returns variable from files in the data/GRID directory
    with grid sorted option
    '''
    if varname in ["Bathymetry"]:
        model_grid = xr.open_dataset(f"../data/GRID/BIOPERIANT12_bathymetry.nc")
        var = model_grid[varname]
    else:    
        meshfile = f"../data/GRID/BIOPERIANT12_grid.nc"   
        model_grid = xr.open_dataset(meshfile, decode_times= False)
        var = model_grid[varname]
        if varname in ['gdept_0']:
            return model_grid.gdept_0[0,:]
        if "t" in var.dims:
            var = var.isel(t=0)
        if is_sorted == 1:
            if "x" in var.dims: var = var.rename({'x':'lon', 'y':'lat'})
            if "z" in var.dims: 
                var = var.rename({'z':'deptht'})
                var = var.assign_coords(deptht=("deptht", model_grid.gdept_0[0,:].values),
                                            lat=("lat", model_grid.nav_lat[:,0].values), 
                                            lon=("lon", model_grid.nav_lon[0,:].values ))
            else:
                var = var.assign_coords(lat=("lat", model_grid.nav_lat[:,0].values), 
                                        lon=("lon", model_grid.nav_lon[0,:].values ))
            var = var.sortby('lon').drop_duplicates('lon', keep='first')    
    return var
            
            
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
            

def make_obs_areagrid(lonin, latin):
    '''
    Calculates the area of each grid cell 
    To define the corner values of latitude and longitude, 
    we need to define the longtiude and latitude steps based on the product's resolution: 
    The below code should therefore be working for any resolution product. 
    Contributing author: A. D. Lebehot Last update: 8 Nov 2019
    '''
    R = 6371000 # Earth Radius (m) 
    area_gridcell = np.ones([len(latin), len(lonin)])
    step_latin = np.abs(latin[0].values - latin[1].values)/2
    step_lonin = np.abs(lonin[0].values - lonin[1].values)/2

    for i in range(len(latin)):
        phi2 = (latin[i].values+step_latin)*pi/180
        phi1 = (latin[i].values-step_latin)*pi/180

        for j in range(len(lonin)):
            lambda2 = (lonin[j].values+step_lonin)*pi/180
            lambda1 = (lonin[j].values-step_lonin)*pi/180

            area_gridcell[i,j] = R*R*(lambda2 - lambda1)*(np.sin(phi2) - np.sin(phi1))
    return area_gridcell
           
def make_obs_areaweight(lonin, latin):
    '''
    Calculates weights of obs grid from grid size
    '''
    area_grid = make_obs_areagrid(lonin, latin)
    totarea = np.sum(area_grid)
    area_weight = area_grid/totarea
    # convert to DataArray
    area_weight_da = xr.DataArray(data=area_weight, dims=["lat", "lon"], 
                              coords=[latin,lonin])
    return area_weight_da


def get_biome_ts(var_in, biome_in, biome_val, vargridarea):
    '''
    Extract biome (biome_val) from xr dataset biome mask (biome_in)
    from a xr dataset with 2d variable field (var_in) 
    with grid area weighting (vargridarea)
    '''
    varbiome = var_in.where(biome_in.values==biome_val)
    var_weighted = varbiome.weighted(vargridarea)
    var_tsmean = var_weighted.mean(("lat", "lon"))
    return var_tsmean