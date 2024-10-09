import sys
sys.path.insert(0, '../')
from bp12_tools.analysis_utils import check_trend
from bp12_tools.plot_utils.formatting import get_biome_colors, get_line_styles, check_colorin

import numpy as np
import xarray as xr
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap

################################################### 
#
# Contains functions used for timeseries plots
# 
################################################### 
def add_seas(axin, ylim_in, is_clim=False, add_legend=False):
    '''
    Add shading for DJF and JAS
    '''
    # Plotting the DJF months
    alpha = 0.3
    if is_clim:
        axin.fill_between([0, 2+1], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#f4a582', alpha=alpha)
        #axin.fill_between([0, 2+1], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#f4a582', alpha=alpha)
    else:
        y=2000
        datestr1, datestr2 = pd.Timestamp(y,1,1), pd.Timestamp(y,2,28)
        axin.fill_between([datestr1, datestr2], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#d8d8d8', alpha=alpha)
        for y in range(2000,2010):
            datestr1, datestr2 = pd.Timestamp(y,12,1), pd.Timestamp(y+1,2,28)
            axin.fill_between([datestr1, datestr2], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#d8d8d8', alpha=alpha)
            #axin.fill_between([datestr1, datestr2], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#d8d8d8', alpha=alpha)
    # Plotting the JAS months
    alpha = 0.2
    if is_clim:
        axin.fill_between([5, 7+1], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#92c5de', alpha=alpha)
        #axin.fill_between([5, 7+1], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#92c5de', alpha=alpha)
    else:
        for y in range(2000,2010):
            datestr1 = pd.Timestamp(y,7,1)
            datestr2  =pd.Timestamp(y,9,30)
            axin.fill_between([datestr1, datestr2], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#92c5de', alpha=alpha)
            #axin.fill_between([datestr1, datestr2], [ylim_in[0], ylim_in[0]], [ylim_in[1], ylim_in[1]], facecolor='#92c5de', alpha=alpha)

    # add legend
    if add_legend:
        handles = [mpatches.Patch(color='#d8d8d8', alpha=0.25), 
                   mpatches.Patch(color='#92c5de', alpha=0.25)]
        leg1 = axin.legend(handles,['DJF','JAS'],
                         bbox_to_anchor=(0.8, 0.95), loc="lower left", ncol=2)
        axin.add_artist(leg1)
        axin.tick_params(labelsize=12)    
    return

#-------------

def plot_ts_3ax(ax, var1_in, var1_minmax, var2_in, var2_minmax, var3_in, var3_minmax, 
                var_cbars, clr_arr, lstylein=None, calc_trend=None):
    '''
    plot timeseries with 3 variables/3 y axes
    '''
    var1_tick, var2_tick, var3_tick = var1_minmax[2], var2_minmax[2], var3_minmax[2]
    var1_cbar, var2_cbar, var3_cbar = var_cbars
    var1_name, var2_name, var3_name = var1_cbar.split(" ")[0], var2_cbar.split(" ")[0], var3_cbar.split(" ")[0]
    tsclr = pf.check_colorin(clr_arr,3)
    lstyle_array = pf.get_line_styles(3)
    if lstylein:
        ls1, ls2, ls3 = lstylein[0], lstylein[1], lstylein[2]
    else:   
        ls1, ls2, ls3 = pu.get_line_styles(3)
        

    ax.plot(var1_in.time, var1_in.values, label='BIOPERIANT12', c=tsclr[0], lw=2, linestyle=ls1, alpha=0.7)
    ax.set_xlim([pd.Timestamp(1999,12,31), pd.Timestamp(2010,1,1)])
    ax.set_ylim([var1_minmax[0], var1_minmax[1]])
    ax.set_yticks(np.arange(var1_minmax[0], var1_minmax[1]+var1_tick, var1_tick))
    ax.set_ylabel(var1_cbar, labelpad=5, fontsize=12)
    _, _, ymin, ymax = ax.axis()
    pu.add_seas(ax, (ymin, ymax), False)

    #add_source(ax)
    #add_var(ax)
    ax.grid()
    ax.tick_params(labelsize=12)
    ax.set_rasterized(True)
    ###--- ax2
    ax2 = ax.twinx()
    ax2.plot(var2_in.time, var2_in.values,  c=tsclr[1], linestyle=ls2, lw=2)
    ax2.set_ylim([var2_minmax[0], var2_minmax[1]])
    ax2.set_yticks(np.arange(var2_minmax[0], var2_minmax[1]+var2_tick, var2_tick))
    ax2.set_ylabel(var2_cbar, labelpad=15, fontsize=12, rotation=-90)
    ax2.yaxis.label.set_color(tsclr[1]) 
    ax2.tick_params(axis='y', colors=tsclr[1]) 
    ax2.set_rasterized(True)

    ax3 = ax.twinx()
    ax3.spines.right.set_position(("axes", 1.12))
    ax3.plot(var3_in.time, var3_in.values, c=tsclr[2], linestyle=ls3, lw=3)
    ax3.set_ylim([var3_minmax[0], var3_minmax[1]])
    ax3.set_yticks(np.arange(var3_minmax[0], var3_minmax[1]+var3_tick, var3_tick))
    ax3.set_ylabel(var3_cbar, labelpad=15, fontsize=12, rotation=-90)
    ax3.yaxis.label.set_color(tsclr[2]) 
    ax3.tick_params(axis='y', colors=tsclr[2]) 
    ax3.set_rasterized(True)
    
    if calc_trend:
        trend = check_trend(var1_in,0)
        if len(trend[0])>1: ax.text(0.0, 0.05, f"{var1_name} {trend[0]} trend p={trend[1]:1.3f}", fontsize=12,
                                         color='k', transform = ax.transAxes)
        trend = check_trend(var2_in,0)
        if len(trend[0])>1: ax.text(0.35, 0.05, f"{var2_name} {trend[0]} trend p={trend[1]:1.3f}", fontsize=12,
                                         color='k', transform = ax.transAxes)
        trend = check_trend(var3_in,0)
        if len(trend[0])>1: ax.text(0.7, 0.05, f"{var3_name} {trend[0]} trend p={trend[1]:1.3f}", fontsize=12,
                                         color='k', transform = ax.transAxes)
        

def plot_ts_2ax(ax, var1_in, var1_minmax, var2_in, var2_minmax, var_cbars, clr_arr, lstylein=None, calc_trend=None):
    '''
    plot timeseries with 2 variables/2 y axes
    '''    
    var1_tick, var2_tick = var1_minmax[2], var2_minmax[2]
    var1_cbar, var2_cbar = var_cbars
    var1_name, var2_name = var1_cbar.split(" ")[0], var2_cbar.split(" ")[0]
    tsclr = check_colorin(clr_arr,2)  
    lstyle_array = get_line_styles(2)
    if lstylein:
        ls1, ls2 = lstyle_array[lstylein[0]], lstyle_array[lstylein[1]]
    else:   
        ls1, ls2 = lstyle_array[0], lstyle_array[1]
    
    ax.plot(var1_in.time, var1_in.values, label='BIOPERIANT12', c=tsclr[0], ls=ls1, lw=2)
    ax.set_xlim([pd.Timestamp(1999,12,31), pd.Timestamp(2010,1,1)])
    ax.set_ylim([var1_minmax[0], var1_minmax[1]])
    ax.set_yticks(np.arange(var1_minmax[0], var1_minmax[1]+var1_tick, var1_tick))
    ax.set_ylabel(var1_cbar, labelpad=5, fontsize=12)
    #ax.yaxis.label.set_color(tsclr[0]) 
    #ax.tick_params(axis='y', colors=tsclr[0]) 
    #add_source(ax)
    #add_var(ax)
    ax.grid(True)
    ax.tick_params(labelsize=12)
    ax.set_rasterized(True)

    ###--- ax2
    ax2 = ax.twinx()
    ax2.plot(var2_in.time, var2_in.values,  c=tsclr[1], ls=ls2, lw=2)
    ax2.set_ylim([var2_minmax[0], var2_minmax[1]])

    ax2.set_yticks(np.arange(var2_minmax[0], var2_minmax[1]+var2_tick, var2_tick))
    _, _, ymin, ymax = ax2.axis()
    add_seas(ax2, (ymin, ymax), False)
    ax2.set_ylabel(var2_cbar, labelpad=25, fontsize=12, rotation=-90)
    ax2.yaxis.label.set_color(tsclr[1]) 
    ax2.tick_params(axis='y', colors=tsclr[1]) 
    ax2.set_rasterized(True)
    
    if calc_trend:
        trend = check_trend(var1_in,0)
        if len(trend[0])>1: ax.text(0.0, 0.05, f"{var1_name} {trend[0]} trend p={trend[1]:1.3f}", fontsize=12,
                                         color='k', transform = ax.transAxes)
        trend = check_trend(var2_in,0)
        if len(trend[0])>1: ax.text(0.35, 0.05, f"{var2_name} {trend[0]} trend p={trend[1]:1.3f}", fontsize=12,
                                         color='k', transform = ax.transAxes)
            
def plot_ts_1ax(axin, var_minmax, tsclr, var_cbar, var_in, lstylein=None, calc_trend=None):
    '''
    plot BP12 timeseries
    '''
    
    lstyle_array=get_line_styles(1)
    var_tick = var_minmax[2]
    if lstylein:
        ls = lstyle_array[lstylein[0]]
    else:   
        ls = lstyle_array[0]
        
    axin.plot(var_in.time, var_in.values, c=tsclr, ls=ls, lw=2)
    axin.set_xlim([pd.Timestamp(1999,12,31), pd.Timestamp(2010,1,1)])
    axin.set_ylim([var_minmax[0], var_minmax[1]])
    axin.set_yticks(np.arange(var_minmax[0], var_minmax[1]+var_tick, var_tick))
    axin.set_ylabel(var_cbar, labelpad=5, fontsize=12)
    axin.tick_params(labelsize=12)
    add_seas(axin, (var_minmax[0], var_minmax[1]), False)
    axin.grid(True)
    axin.set_rasterized(True)

    if calc_trend:
        vname = var_cbar.split(" ")[0]
        trend = bp12.analysis_utils.check_trend(var_in,0)
        if len(trend[0])>1: axin.text(0.05, 0.85, f"{vname} {trend[0]} trend p={trend[1]:1.3f}", fontsize=12,
                                         color='k', transform = axin.transAxes)
            
def plot_ts_mdlvsobs(ax, mdl_in, obs_in, var_minmax, clr_arr, var_cbar, lstylein=None, calc_trend=None):
    '''
    plot BP12 vs OBS timeseries
    '''
    var_tick = var_minmax[2]
    tsclr = check_colorin(clr_arr,2)  
    lstyle_array=get_line_styles(2)
    var_tick = var_minmax[2]
    if lstylein:
        ls1, ls2 = lstyle_array[lstylein[0]], lstyle_array[lstylein[1]]
    else:   
        lstyle_array = ['-', '--'] #get_line_styles(2)
    
    ax.plot(mdl_in.time, mdl_in.values, c=tsclr[0], ls=ls1, lw=2, label='BIOPERIANT12')
    ax.plot(obs_in.time, obs_in.values, c=tsclr[1], ls=ls2, lw=2, label='OBS')
    ax.set_xlim([pd.Timestamp(1999,12,31), pd.Timestamp(2010,1,1)])
    ax.set_ylim([var_minmax[0], var_minmax[1]])
    ax.set_yticks(np.arange(var_minmax[0], var_minmax[1], var_tick))
    ax.set_ylabel(var_cbar, labelpad=5, fontsize=12)
    ax.grid(True)
    ax.tick_params(labelsize=12)
    add_seas(ax, (var_minmax[0], var_minmax[1]), False)
    ax.set_rasterized(True)
    
    if calc_trend:
        vname = var_cbar.split(" ")[0]
        trend = check_trend(mdl_in,0)
        if len(trend[0])>1: 
            ax.text(0.05, 0.85, f"{vname} {trend[0]} trend p={trend[1]:1.3f}", \
                    fontsize=12, color='k', transform = ax.transAxes)
            

            

#-------------- A d d --- l e g e n d s ---------------          
            
def add_var_leg_3ax(axin, posin, var_lbls, colorin=None, lstylein=None):
    '''
    add legend for timeseries with 3 variables/3 y axes
    '''
    if not colorin: 
        color1, color2, color3 = 'k', 'k', 'k'
    else:
        color1, color2, color3 = check_colorin(colorin,3)
    lstyle_array = get_line_styles(3)     
    if not lstylein or len(lstylein) < 3: 
        lstyle0, lstyle1, lstyle2 = lstyle_array[0:3] 
    else:
        lstyle0, lstyle1, lstyle2 = lstyle_array[lstylein[0]], lstyle_array[lstylein[1]],  lstyle_array[lstylein[2]]


    var1_lbl, var2_lbl, var3_lbl = var_lbls
    var1_l = mpl.lines.Line2D([], [], color=color1, linestyle=lstyle0, alpha=0.7,      label=var1_lbl)
    var2_l = mpl.lines.Line2D([], [], color=color2, linestyle=lstyle1, label=var2_lbl)
    var3_l = mpl.lines.Line2D([], [], color=color3, linestyle=lstyle2, label=var3_lbl)
    legv = axin.legend(handles=[var1_l, var2_l, var3_l], fontsize=12, ncol=3,
                   bbox_to_anchor=posin, loc="lower left", frameon=True)
    axin.add_artist(legv)
    return
    
def add_var_leg_2ax(axin, posin, lblin, colorin=None, lstylein=None):
    '''
    add legend for timeseries with 2 variables/2 y axes
    '''
    if not colorin: 
        color1, color2 = 'k', 'k'
    else:
        color1, color2 = check_colorin(colorin,2)
    lstyle_array =  get_line_styles(2)       
    if not lstylein or len(lstylein) < 2: 
        lstyle0, lstyle1 = lstyle_array[0:2] 
    else:
        lstyle0, lstyle1 = lstyle_array[lstylein[0]], lstyle_array[lstylein[1]]
    
    line_1 = mpl.lines.Line2D([], [], color=color1, lw=2, ls=lstyle0, label=lblin[0])
    line_2 = mpl.lines.Line2D([], [], color=color2, lw=2, ls=lstyle1, label=lblin[1])
    leg1 = axin.legend(handles = [line_1, line_2], ncol=2, fontsize=12,
                  bbox_to_anchor=posin, loc="lower left",frameon=True)
    axin.add_artist(leg1)

def add_var_leg_mdlobs(axin, posin, lblin, colorin=None, yesframe=None):
    '''
    add legend for model vs obs timeseries
    '''
    if not colorin: 
        color1, color2 = 'k', 'k'
    else:
        color1, color2 = check_colorin(colorin,2)
        
    yesframe=False if not yesframe else True
        
    line_1 = mpl.lines.Line2D([], [], color=color1, lw=2, label=lblin[0])
    line_2 = mpl.lines.Line2D([], [], color=color2, lw=2, label=lblin[1])
    leg1 = axin.legend(handles = [line_1, line_2], ncol=2, fontsize=12,
                  bbox_to_anchor=posin, loc="lower left",frameon=yesframe)
    axin.add_artist(leg1)
    
    
def add_biome_legend(axin, posin, ncolin):
    '''add legend for biomes'''
    color17 = get_biome_colors(17)
    color16 = get_biome_colors(16)
    color15 = get_biome_colors(15)  

    biome17 = mpl.lines.Line2D([], [], color=color17, label='SO-ICE', marker='o', linestyle='None', markersize=10)
    biome16 = mpl.lines.Line2D([], [], color=color16, label='SO-SPSS',  marker='o', linestyle='None', markersize=10)
    biome15 = mpl.lines.Line2D([], [], color=color15, label='SO-STSS',  marker='o', linestyle='None', markersize=10)
    leg2 = axin.legend(handles=[biome17, biome16, biome15], fontsize=10,
                   bbox_to_anchor=posin, labelspacing=0.5,
                   loc="lower left", ncol=ncolin, frameon=False)
    axin.add_artist(leg2)
    
    
def add_omlegend(axin, posin, colrin='k'):
    '''
    add legend for obs/model
    '''
    line_mdl = mpl.lines.Line2D([], [],  color=colrin, lw=2, label='BIOPERIANT12')
    line_obs  = mpl.lines.Line2D([], [], color=colrin, lw=3, linestyle='--', label='OBS')
    leg1 = axin.legend(handles = [line_mdl,line_obs], ncol=2, fontsize=12, 
                      bbox_to_anchor=posin, loc="lower left",frameon=False)
    axin.add_artist(leg1)

    