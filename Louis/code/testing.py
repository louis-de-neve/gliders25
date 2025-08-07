from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import xarray as xr
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
from scipy.stats import linregress
from matplotlib.legend_handler import HandlerTuple
from matplotlib.patches import FancyBboxPatch
import cmocean
import cmweather
import xlrd
import cmcrameri.cm as cmc

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


def make_cmap(cmi):
    cmap = mpl.colormaps['CM_rhohv_r']
    cmap = cmocean.tools.crop_by_percent(cmap, 8, 'max')
    cmap_rgba = cmap(np.linspace(0, 1, abs(cmin)))
    cmap_rgba[:, 3] = 1  # set alpha to 1
    mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', cmap_rgba)
    return mymap



cmin, cmax = -8000, 0
cmap = make_cmap(cmin)


#fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
fig = plt.figure(figsize=(13, 6))  # Landscape orientation
main_ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])      # Main map on the right


# Load data
dataset = xr.open_dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc', engine="netcdf4")

x = dataset.variables['lon']
y = np.asarray(dataset.variables['lat'])
Z = np.asarray(dataset.variables['elevation'])
m = Basemap(llcrnrlon=-40,llcrnrlat=-62.0,urcrnrlon=-34,urcrnrlat=-59.0,
            resolution='i',projection='merc',lon_0=-15.0,lat_0=55.0, ax=main_ax)



x,y = m(*np.meshgrid(x,y))
bmp = m.pcolormesh(x, y, Z, cmap=cmap, vmin=cmin, vmax=cmax)


contour = m.contour(x, y, Z, levels=[-3100], colors='#00000000', ax=main_ax)
vs = (contour.collections[0].get_paths()[0].vertices)
vs = vs[4970:8910]
plt.plot(vs[:, 0], vs[:, 1], c="black", linestyle="dashed")



plt.show()

