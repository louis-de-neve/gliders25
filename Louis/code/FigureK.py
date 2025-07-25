from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap
import xarray as xr
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
from scipy.stats import linregress
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

def map_plot(profiles:list[Profile], colour_parameter:str, ax, variable_limit=None, basemap=None) -> None:

        
    longitudes = np.asarray([p.start_location[0] for p in profiles if p.active_zone>100])
    latitudes = np.asarray([p.start_location[1] for p in profiles if p.active_zone>100])
    colors = np.asarray([p.active_zone for p in profiles if p.active_zone>100])


    
    if basemap != None:
        longitudes, latitudes = basemap(longitudes, latitudes)
    pcm = ax.scatter(longitudes, latitudes, c=colors, s=15, cmap="viridis", norm=mpl.colors.Normalize(vmin=100, vmax=200))
    return pcm
    




#fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
fig = plt.figure(figsize=(12,6))
main_ax = fig.add_axes([0.05, 0.2, 0.4, 0.79])  # [left, bottom, width, height]
bottom_ax = fig.add_axes([0.125, 0.1, 0.25, 0.02])  # [left, bottom, width, height]
side_ax = fig.add_axes([0.92, 0.3, 0.01, 0.5])  # [left, bottom, width, height]
axes = [main_ax, bottom_ax, side_ax]

# Add second main_ax and bottom_ax
second_main_ax = fig.add_axes([0.5, 0.2, 0.4, 0.79])  # [left, bottom, width, height]
second_bottom_ax = fig.add_axes([0.575, 0.1, 0.25, 0.02])  # [left, bottom, width, height]
axes.append(second_main_ax)
axes.append(second_bottom_ax)

# Load data
dataset = xr.open_dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc', engine="netcdf4")

x = dataset.variables['lon']
y = np.asarray(dataset.variables['lat'])
Z = np.asarray(dataset.variables['elevation'])
m = Basemap(llcrnrlon=-40,llcrnrlat=-62.0,urcrnrlon=-34,urcrnrlat=-59.0,
            resolution='i',projection='merc',lon_0=-15.0,lat_0=55.0, ax=axes[0])
x,y = m(*np.meshgrid(x,y))

original_cmap = mpl.colormaps["gist_gray"]
colors = original_cmap(np.arange(original_cmap.N))
colors[:, -1] = 0.6  # Set alpha
modified_cmap = ListedColormap(colors, "modified_cmap")
bmp = m.contourf(x, y, Z, cmap=modified_cmap)

###

# Add second map

m2 = Basemap(llcrnrlon=-40,llcrnrlat=-62.0,urcrnrlon=-34,urcrnrlat=-59.0,
            resolution='i',projection='merc',lon_0=-15.0,lat_0=55.0, ax=axes[3])


original_cmap = mpl.colormaps["gist_gray"]
colors = original_cmap(np.arange(original_cmap.N))
colors[:, -1] = 0.6  # Set alpha
modified_cmap = ListedColormap(colors, "modified_cmap")
bmp = m2.contourf(x, y, Z, cmap=modified_cmap)

###





m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])


m2.fillcontinents(color='grey')
m2.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m2.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])



pcm = map_plot(profiles, "bbp_minimum_despiked", axes[0], variable_limit=None, basemap=m)
axes[0].set_xlabel("Longitude", labelpad=15)
axes[0].set_ylabel("Latitude")

plt.colorbar(pcm, cax=axes[1], orientation="horizontal")
axes[1].set_xlabel(r"High Chlorophyll Zone Depth (m)")




axes[2].invert_xaxis()
plt.colorbar(bmp, cax=axes[2], orientation="vertical")
axes[2].set_ylabel(r"Depth (m)")
xticks = axes[2].get_xticks()
axes[2].set_xticklabels([int(abs(tick)) for tick in xticks])


def map_plot2(profiles:list[Profile], colour_parameter:str, ax, variable_limit=None, basemap=None) -> None:

        
    longitudes = np.asarray([p.start_location[0] for p in profiles if p.active_zone>100])
    latitudes = np.asarray([p.start_location[1] for p in profiles if p.active_zone>100])
    colors = np.asarray([(p.active_zone - p.photic_depth) for p in profiles if p.active_zone>100])
    print(colors)

    
    if basemap != None:
        longitudes, latitudes = basemap(longitudes, latitudes)
    pcm = ax.scatter(longitudes, latitudes, c=colors, s=15, cmap="magma", norm=mpl.colors.Normalize(vmin=30, vmax=130))
    return pcm
    

pcm = map_plot2(profiles, "bbp_minimum_despiked", axes[3], variable_limit=None, basemap=m)
axes[3].set_xlabel("Longitude", labelpad=15)
axes[3].set_ylabel("Latitude")

plt.colorbar(pcm, cax=axes[4], orientation="horizontal")
axes[4].set_xlabel(r"Extent of High Chlorophyll Zone beyond Photic Zone (m)")










#fig.tight_layout()
plt.savefig("Louis/figures/figureK.png", dpi=300)
