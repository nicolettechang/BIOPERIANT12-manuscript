import numpy as np
import xarray as xr
import pandas as pd

import sys
sys.path.insert(0, '../')
from bp12_tools.plot_utils.formatting import get_biome_colors, get_rbg_colors
from bp12_tools.analysis_utils import pfloor, pceil

from cartopy import crs as ccrs, feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

import matplotlib.colors as clr
from matplotlib.colors import ListedColormap
import matplotlib as mpl
import matplotlib.font_manager

import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


################################################### 
#
# Contains functions used for plotting maps
#
################################################### 


########### Map plotting #########################
def map_decorator(axin):
    '''
    In a cartopy stereographic map add coast, land and gridlines
    '''
    land_feature, coast_feature = get_cartopy_landcoast()
    axin.gridlines(alpha=1, linewidth=0.35, linestyle='--', ylocs=np.arange(-80,0,10))
    axin.set_global()
    axin.set_extent([-180, 180, -90, -30], ccrs.PlateCarree())
    axin.add_feature(land_feature, color='white', zorder=10)
    axin.add_feature(coast_feature, lw=2, color='k', zorder=8)
    gl = axin.gridlines(draw_labels=False,color='k',lw=0.1,alpha=0.4)
    axin.outline_patch.set_edgecolor('darkgrey')
    axin.outline_patch.set_linewidth(1.5)
    axin.set_rasterized(True)
    
def get_cartopy_landcoast():
    '''
    Returns local coast and land shapefiles for cartopy plots
    '''
    coastfile = f'../data/cartopy_shapefiles/ne_10m_coastline.shp'
    coast_feature = ShapelyFeature(Reader(coastfile).geometries(),
                                     ccrs.PlateCarree(), lw=1.5, edgecolor='k', facecolor='w')

    landfile = f'../data/cartopy_shapefiles/ne_10m_land.shp'
    land_feature = ShapelyFeature(Reader(landfile).geometries(),
                                     ccrs.PlateCarree(), color='w')
    return land_feature, coast_feature

def get_cmap_mask():
    '''
    Return grey colormap for adding mask
    to lat/lon plot
    '''
    cmap = plt.cm.gray
    cmap_mask = cmap(np.arange(cmap.N))
    cmap_mask[:,-1] = np.linspace(0, 1, cmap.N) * 0.6
    cmap_mask = ListedColormap(cmap_mask)
    return cmap_mask

def add_coast(axin):
    '''
    add land shading for geographic context 
    '''
    coast_ds = xr.open_dataset(f"../data/GRID/BIOPERIANT12_coastline.nc")
    _, _, ymin, ymax = axin.axis()
    ymin, ymax = pfloor(ymin,0), pceil(ymax,0)
    #ax2.set_ylim([ymin, ymax])
    yrange = ymax-ymin
    a = ymin + (yrange/2) + (coast_ds.sa_coast * yrange/2)
    amax = a.copy()
    amax['sa_coast'] = ymax
    b = ymin + coast_ds.aa_coast*yrange/4
    bmin = b.copy()
    bmin['aa_coast'] = ymin
    axin.fill_between(a.lon, a, amax.sa_coast, alpha=0.1, facecolor='grey', zorder=10)
    axin.fill_between(b.lon, bmin.aa_coast, b, alpha=0.1, facecolor='grey', zorder=10)
    return
  
def add_fronts(axin, ind, dataset="mdl"):
    '''
    plot climatological fronts on a stereographic map
    from model or observations
    ind = month or -1 = annual mean
    '''
    if dataset == "mdl":
        ds_saf = xr.open_dataset(f"../data/FRONTS/BIOPERIANT12_SAF_clim_monthly.nc")
        ds_pf  = xr.open_dataset(f"../data/FRONTS/BIOPERIANT12_PF_clim_monthly.nc")
        fcol=get_rbg_colors('r')
    elif dataset == "obs":
        ds_saf = xr.open_dataset(f"../data/FRONTS/WOA13_SAF_clim_monthly.nc")
        ds_pf  = xr.open_dataset(f"../data/FRONTS/WOA13_PF_clim_monthly.nc")
        fcol=get_rbg_colors('b')
        
    if ind > 0:
        saf, pf = ds_saf.lat[ind,:], ds_pf.lat[ind,:]
    else:
        saf, pf = ds_saf.lat.mean('time'), ds_pf.lat.mean('time')
    axin.plot(saf.lon, saf, color=fcol, 
            linestyle='--', alpha=0.7, transform=ccrs.PlateCarree(), zorder=10)
    axin.plot(pf.lon, pf, color=fcol, alpha=0.9, transform=ccrs.PlateCarree(), zorder=10)
    return

def add_biomes(axin, dataset="mdl", alph=0.9):
    '''
    plot climatological biomes on a stereographic map
    from model or FK2014
    '''
    if dataset == "mdl":
        ds_bdy = xr.open_dataset(f"../data/BIOMES/BIOPERIANT12_biome_bdy_clim.nc")
    elif dataset == "obs":
        ds_bdy = xr.open_dataset(f"../data/BIOMES/OBS_biome_bdy_clim.nc")
        
    for biome in [15,16,17]:
        biome_color = get_biome_colors(biome)
        bdy = ds_bdy[f"b{biome}_nbdy"]
        axin.plot(bdy.lon, bdy, color=biome_color, alpha=alph, transform=ccrs.PlateCarree(), zorder=8)
    return


    