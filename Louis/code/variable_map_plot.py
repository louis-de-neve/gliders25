import matplotlib.pyplot as plt
from setup import import_split_and_make_transects, Transect, Profile
from preprocessing.apply_preprocessing import scatter_and_chlorophyll_processing
from preprocessing.chlorophyll.default_quenching import default_quenching_correction
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.axes as mpl_axes
from matplotlib.colors import ListedColormap
import xarray as xr
from mpl_toolkits.basemap import Basemap


transects, all_valid_profiles = import_split_and_make_transects(use_cache=True,
                                                                use_downcasts=True,)


def map_plot(profiles:list[Profile], colour_parameter:str, ax:mpl_axes.Axes, variable_limit=None, basemap=None) -> None:

        
    longitudes = np.asarray([p.start_location[0] for p in profiles])
    latitudes = np.asarray([p.start_location[1] for p in profiles])
    colors = np.asarray([p.active_zone for p in profiles])


    
    if basemap != None:
        longitudes, latitudes = basemap(longitudes, latitudes)
    pcm = ax.scatter(longitudes, latitudes, c=colors, s=15, cmap="turbo", norm=mpl.colors.Normalize(vmin=100, vmax=250))
    return pcm
    




#fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
fig = plt.figure(figsize=(6,6))
main_ax = fig.add_axes([0.1, 0.2, 0.7, 0.7])  # [left, bottom, width, height]
bottom_ax = fig.add_axes([0.1, 0.1, 0.7, 0.02])  # [left, bottom, width, height]
side_ax = fig.add_axes([0.82, 0.2, 0.02, 0.7])  # [left, bottom, width, height]
ax = [main_ax, bottom_ax, side_ax]

# Load data
dataset = xr.open_dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc', engine="netcdf4")

x = dataset.variables['lon']
y = np.asarray(dataset.variables['lat'])
Z = np.asarray(dataset.variables['elevation'])
m = Basemap(llcrnrlon=-40,llcrnrlat=-62.0,urcrnrlon=-34,urcrnrlat=-59.0,
            resolution='i',projection='stere',lon_0=-15.0,lat_0=55.0, ax=ax[0])
x,y = m(*np.meshgrid(x,y))

original_cmap = mpl.colormaps["gist_gray"]
colors = original_cmap(np.arange(original_cmap.N))
colors[:, -1] = 0.7  # Set alpha
modified_cmap = ListedColormap(colors, "modified_cmap")
bmp = m.contourf(x, y, Z, cmap=modified_cmap)


m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])



pcm = map_plot(all_valid_profiles, "bbp_minimum_despiked", ax[0], variable_limit=None, basemap=m)
ax[0].set_xlabel("Longitude", labelpad=15)
ax[0].set_ylabel("Latitude")

plt.suptitle(r"Biologically active zone map")
plt.colorbar(pcm, cax=ax[2], orientation="vertical")
ax[2].set_ylabel(r"Active Zone Depth$ (m)")




ax[1].invert_xaxis()
plt.colorbar(bmp, cax=ax[1], orientation="horizontal")
ax[1].set_xlabel(r"Depth (m)")
xticks = ax[1].get_xticks()
ax[1].set_xticklabels([int(abs(tick)) for tick in xticks])











#plt.tight_layout()
plt.savefig("Louis/outputs/variable_map_plot.png", dpi=300)
#plt.show()



#PHOTIC ZONE TESTING
# zero = np.zeros(len(hues))
# plt.plot(hues, color="green", alpha=0.5)
# plt.fill_between(np.arange(len(hues)), hues_below, hues, color="green", alpha=0.5, label="Above Photic Zone")
# plt.plot(hues_below, color="red", alpha=0.5)
# plt.fill_between(np.arange(len(hues)), zero, hues_below, color="red", alpha=0.5, label="Below Photic Zone")
# plt.legend()

# plt.savefig("Louis/outputs/depth_integrated_chlorophyll_photic.png", dpi=300)
# plt.show()


#QUICK REGRESSION TESTING
# plt.scatter(hues_above, hues_below, color="black", alpha=0.5, marker="x")
# plt.xlabel("Chlorophyll Above Photic Zone")
# plt.ylabel("Chlorophyll Below Photic Zone")
# slope, intercept, r_value, p_value, std_err = linregress(hues_above, hues_below)
# plt.plot(hues_above, slope * np.array(hues_above) + intercept, color="blue", label=f"y={slope:.2f}x+{intercept:.2f}\nR²={r_value**2:.2f}")
# plt.legend()
# plt.show()