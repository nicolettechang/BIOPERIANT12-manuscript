__version__ = "0.0"
__author__ = "Nicolette Chang"

__all__ = ["maps", "timeseries", "formatting"]

# Set global matplotlib params
import matplotlib as mpl
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['figure.figsize'] = [10, 5]
mpl.rcParams['font.size'] = 12
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['axes.titlesize'] =12
mpl.rcParams['axes.labelsize'] =10

# Import the submodules
from . import maps
from . import timeseries
from . import formatting
