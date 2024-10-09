import numpy as np
import sys
sys.path.insert(0, '../')
from bp12_tools.model_utils import get_varinfo
from bp12_tools.analysis_utils import pfloor, pceil
###########################################
#
# Options for plot formatting 
#
###########################################    


########## string formatting ################    
    
def get_unit_mplstr(unit_name):
    '''
    return units in format for matplotlib labels
    '''
    if unit_name=="cm2s2": return "[cm$^2$ s$^{-2}$]"  
    elif unit_name=="degC": return "[\u00b0C]"
    elif unit_name=='jm2': return '[10$^9$ J m$^{-2}$]'
    elif unit_name=='mgm3': return '[mg m$^{-3}$]'
    elif unit_name=="mmolperl": return"[mmol l$^{-1}]$"
    elif unit_name=='molm2peryr': return "[mol m$^{-2}$ yr$^{-1}$]"
    elif unit_name=='uatm': return '[$\mu$atm]'
    elif unit_name=="umolperl": return "[\u03BCmol l$^{-1}$]"
    elif unit_name=="nmolperl": return "[nmol l$^{-1}$]"
    elif unit_name=="umolkg": return "[\u03BCmol kg$^{-1}$]"
    elif unit_name=="mgm2perd": return "[mgC m$^{-2}$ d$^{-1}$]"
    elif unit_name=="percent": return "[%]"
    else: return f"[{unit_name}]"

def get_name_mplstr(vname):
    '''
    return var name in format for matplotlib labels
    '''
    if vname in ["pco2", "PCO2", "pCO2"]: return "pCO$_2$"  
    elif vname in ["fco2", "FCO2", "FCO2"]: return "FCO$_2$"  
    elif vname in ["no3", "NO3"]: return "NO$_3$" 
    elif vname in ["po4", "PO4"]: return "PO$_4$" 
    elif vname in ["o2", "O2"]: return "O$_2$" 
    else: return vname

def get_label_mplstr(vname):
    '''
    return var name and unit format for matplotlib labels
    '''
    vnstr = get_name_mplstr(vname)
    unstr = get_unit_mplstr(get_varinfo(vname, 'unit'))
    return f"{vnstr} {unstr}"
    
def get_mo_titles(start_seas=None):
    '''
    Return month prefixes for timeseries labels
    '''       
    if start_seas in ["JFM", "jfm"]:
        return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    else:
        return ['Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun']


def get_xylim(minval, maxval, prec=None):
    '''
    get neat limits of the axis with floats
    '''
    if (prec is None) and (np.abs(maxval-minval) > 1.5):
        return np.floor(minval), np.ceil(maxval)
    else:
        return pfloor(minval,prec), pceil(maxval,prec)

########## C o l o u r s ################

def get_biome_colors(biomenum, isFM2014=None):
    '''
    Return color code for specific biomes
    isFM2014 - uses Fay&McKinley(2014) like color palette
    else uses inclusive color palette fro internet
    '''
    if isFM2014:
        newcolors = np.empty([6,4])
        RR = [110, 236, 233,   0,   0,  67,  67]
        GG = [ 39,  49, 228, 160, 157, 102, 102]
        BB = [ 73,  76,   0,  77, 215, 180, 180]
        newcolors = np.c_[RR, GG, BB] / 255
    else:
        newcolors = ["#003a7d","#f9e858","#c701ff","#ff9d3a","#ff73b6","#008dff","#008dff"]
    bounds = np.array([7, 13, 14, 15, 16, 17, 18])
    if biomenum in bounds:
        indx = np.where(bounds==biomenum)[0][0]
        return newcolors[indx]
    else:
        return "k"
       
def check_colorin(color_arr: list, ncolors: int) -> list:
    '''
    Make array of colors to plot 
    of size = ncolors 
    from color_arr = an array of colors
    if list of colors is not a list returns all black
    '''
    if not isinstance(color_arr, list):
        return ['k' for i in range(ncolors)]
        
    n_color_arr = len(color_arr)
    if n_color_arr==1:
        colorsout = [color_arr[0] for i in range(ncolors)]
    elif n_color_arr>1:
        colorsout = []
        for i in range(max(n_color_arr,ncolors)):
            if i==ncolors:
                break
            if i < n_color_arr:
                colorsout.append(color_arr[i])
            else:
                colorsout.append('k')
    return colorsout
    

def get_rbg_colors(clr_in):
    '''
    Return color hex code for red blue green
    '''
    if clr_in in ['r', 'R']:
        return '#cc2d35'
    elif clr_in in ['b', 'B']:
        return '#0063c5'
    elif clr_in in ['g', 'G']:
        return "#4cb23b"
    else:
        return 'k'
    
def get_line_styles(nstyles):
    '''
    Return n disparate line styles
    '''
    lstyle_array = ["-", "--", ":", "-.", "-", "--", ":", "-."]
    return lstyle_array[:nstyles]

    
########### Image formatting #########################  
from PIL import ImageChops
def trim_whitespace(im):
    '''
    Crop white space around image
    '''
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    