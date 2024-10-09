import pandas as pd
import numpy as np
import xarray as xr
import re
import os
from pathlib import Path

################################################################################### 
#
# Contains functions for data sorting and manipulation specific to BP12 model output
#
################################################################################### 

def get_mmdd_5d(yr):
    '''
    Gets a string for the dates of model 5d averages from a 
    365 day calendar for the specified year.
    '''
    ts = []
    for mo in range(1,13):
            if mo in [1,4,5]:
                D= [5,10,15,20,25,30]
            elif mo ==2:
                D=[4,9,14,19,24]
            elif mo in [3,12]:
                D=[1,6,11,16,21,26,31]
            elif mo in [6,7]:
                D=[4,9,14,19,24,29]
            elif mo == 8:
                D=[3,8,13,18,23,28]
            elif mo in [9,10]:
                D=[2,7,12,17,22,27]
            elif mo in [11]:
                D=[1,6,11,16,21,26]
            for dd in D:
                ts.append(f"y{yr}m{mo:02}d{dd:02}")
    return ts

def make_timeaxis_5d(y1,y2):   
    '''
    Gets a list of pandas timestamps corresponding to 
    the dates of model 5d averages on a 365 day calendar 
    for the specified year range.
    '''
    yr1, yr2 = int(y1), int(y2)
    ts = []
    for yr in range(yr1, yr2+1):
        for dstr in get_mmdd_5d(yr): 
            ts.append(pd.Timestamp(int(dstr[1:5]), int(dstr[6:8]), int(dstr[9:11]) ,12))
    return ts
  
def get_filetype(varin):
    '''
    Lazy way to get the file a variable is stored in,
    helps substitute file type in my many loops
    '''
    if varin in ['votemper', 'vosaline', 'sossheig', 'somxl010', 'sohefldo', 
                 'soshfldo', 'sowaflup', 'sowafldp', 'iowaflup', 'sowaflcd', 
                 'solhflup', 'solwfldo', 'sosbhfup']:
        return "gridT"
    if varin in['DIC','Alkalini','O2','CaCO3','PO4','POC','Si','PHY',
            'ZOO','DOC','PHY2','ZOO2','DSi','Fer','BFe','GOC',
            'SFe','DFe','GSi','NFe','NCHL','DCHL','NO3','NH4',
            'chl','CHL']:
        return "ptrcT"
    if varin in ['Cflx','Oflx','Kg','Delc','PMO','PMO2','ExpFe1','ExpFe2',
                 'ExpSi','ExpCaCO3','heup','Fedep','Nfix','PH','CO3',
                 'CO3sat','PAR','PPPHY','PPPHY2','PPNEWN','PPNEWD',
                 'PBSi', 'PFeN', 'PFeD','pp','PP']:
        return "diadT"
    if varin in ['isnowthi','iicethic','iiceprod','ileadfra','iicetemp','ioceflxb',
                 'iocesafl','iicevelu','iicevelv','iocestru','iocestrv',
                 'iicestru','iicestrv','isursenf','isurlatf','isurlowf',
                 'isurshwf','iicesenf','iicelatf']:
        return "icemod"
    if varin in ['solhflup', 'solwfldo', 'sosbhfup', 'soshfldo', 'sohefldo', 
                 'sohefldp', 'sowaflup', 'sowaflcd', 'sowafldp', 'sohumspe', 'sotemair', 
                 'sowindsp', 'sowapre', 'soccov', 'sornf']:
        return "flxT"
    if varin in ['vozocrtx', 'sozotaux']:
        return "gridU"
    if varin in ['vomecrty', 'sometauy' ]:
        return "gridV"
    if varin in ['vovecrtz', 'votkeavt']:
        return "gridW"
    return None

def find_ind(coord, grid1d):
    '''
    return the index of the coord on a 1d grid
    '''                       
    a=abs(grid1d-coord)
    return np.where(a==np.min(a))[0][0]

def get_weightmodel(is_sorted=1):
    '''
    returns area weights for model grid
    if is_sorted is one a sorted dataarray with coordinates is returned
    else uses the default output 
    '''
    meshfile = f"../data/GRID/BIOPERIANT12_grid.nc"
    model_grid = xr.open_dataset(meshfile, decode_times= False) 
    
    tmask = model_grid.tmask[0,0,:] 
    e1t = model_grid.e1t[0,0,:] 
    e2t = model_grid.e2t[0,0,:]
    area_model = tmask * e1t * e2t
    
    if is_sorted == 1:
        area_model = area_model.rename({'y':'lat', 'x':'lon'})
        area_model = area_model.assign_coords(lat=("lat", model_grid.nav_lat[:,0].values), 
                                              lon=("lon", model_grid.nav_lon[0,:].values))
        area_model = area_model.sortby('lon').drop_duplicates('lon', keep='first') 
    
    total_area_model = np.sum(area_model)
    weight_model = area_model/total_area_model
    return weight_model

def get_varinfo(vname_in, key_in):
    '''
    return info needed to plot variables
    e.g. coeff, units, etc.
    '''
    vname_in = vname_in.lower()
    vname_info = {
        'votemper': {'long_name':'Temperature', 'short_name':'T', 'unit':'degC', 'mcoef':1, 'ocoef':1},
        'vosaline': {'long_name':'Salinity', 'short_name':'S', 'unit':' ', 'mcoef':1, 'ocoef':1},
        'somxl010': {'long_name':'Mixed layer depth', 'short_name':'MLD', 'unit':'m', 'mcoef':1, 'ocoef':1},
        'eke': {'long_name':'EKE', 'short_name':'EKE', 'unit':'cm2s2', 'mcoef':1e4, 'ocoef':1e4},
        'ohc': {'long_name':'Heat content', 'short_name':'OHC', 'unit':'jm2', 'mcoef':1e-9, 'ocoef':1e-9},
        'no3': {'long_name':'Nitrate',  'short_name':'NO3', 'unit':'mmolperl', 'mcoef':131147.540983607, 'ocoef':1},
        'po4': {'long_name':'Phosphate','short_name':'PO4','unit':'mmolperl', 'mcoef':8196.7213114754, 'ocoef':1},
        'o2': {'long_name':'Dissolved Oxygen', 'short_name':'O2','unit':'umolperl', 'mcoef':1e6, 'ocoef':43.570*1.03},
        'si': {'long_name':'Silicate', 'short_name':'Si', 'unit':'mmolperl', 'mcoef':1e6, 'ocoef':1},
        'fer': {'long_name':'Diss. Iron', 'short_name':'DFe','unit':'nmolperl', 'mcoef':1e9, 'ocoef':1},    
        'dic': {'long_name':'Dissolved Inorganic Carbon', 'short_name':'DIC', 'unit':'umolkg', 
                'mcoef':1e6*(1/1.024), 'ocoef':1},
        'alkalini': {'long_name':'Total Alkalinity', 'short_name':'TA', 'unit':'umolkg', 
                     'mcoef':1e6*(1/1.024), 'ocoef':1},    
        'fco2': {'long_name':'Air–sea flux of CO$_2$', 'short_name':'FCO2', 'unit':'molm2peryr', 'mcoef':1, 'ocoef':1},
        'pco2': {'long_name':'Partial Pressure of CO$_2$', 'short_name':'pCO2', 'unit':'uatm', 'mcoef':1, 'ocoef':1},
        'chl': {'long_name':'Total chlorophyll-a', 'short_name':'Tot. chl', 'unit':'mgm3', 'mcoef':1e6, 'ocoef':1},
        'pp': {'long_name':'Total primary production', 'short_name':'Tot. PP', 'unit':'mgm2perd', 'mcoef':12.01071*24*3600*6, 'ocoef':1}, 
        'ileadfra': {'long_name':'Ice fraction', 'short_name':'Ice', 'unit':'percent', 'mcoef':1, 'ocoef':1},
        'iicethic': {'long_name':'Ice thickness', 'short_name':'Ice', 'unit':'m', 'mcoef':1, 'ocoef':1} 
    }
    # check if works
    if vname_info.get(vname_in):
        return vname_info.get(vname_in)[key_in]
    else:
        if key_in in ['unit','long_name']:
            return ""
        else:
            return 1