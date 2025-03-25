import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Transect, Profile
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction
from plotting_functions import binned_plot
import numpy as np
import pandas as pd
import matplotlib as mpl
from scipy.stats import linregress
import matplotlib.axes as mpl_axes
from matplotlib.colors import ListedColormap
import netCDF4
import xarray as xr
from mpl_toolkits.basemap import Basemap


transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_cache=True,
                                                                use_supercache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=True,
                                                                despiking_method="minimum")

def map_plot(profiles:list[Profile], colour_parameter:str, ax:mpl_axes.Axes, variable_limit=None, basemap=None) -> None:
    longitudes, latitudes, hues, all_hues = [], [], [], []
    for p in profiles:
        if p.direction == "up" and p.data["depth"].max() >= 500:
            data = p.data.sort_values("depth")
            data = data[data["depth"] > 1]
            data = data[data["depth"] <= 500]

            if variable_limit is not None:
                data = variable_limit(p, data)
                
            xs = np.asarray(data["depth"])
            ys = np.asarray(data[colour_parameter])
            ys = np.nan_to_num(ys)
            integral = np.trapezoid(ys, x=xs)

            if integral > .00001:
                hues.append(data[colour_parameter].mean()) # METHOD FOR BBP ONLY
                #hues.append(integral) # CHLORPHYLL METHOD
                longitudes.append(p.start_location[0])
                latitudes.append(p.start_location[1])
            all_hues.append(integral)
          
    hues = np.asarray(hues)

    
    if basemap != None:
        longitudes, latitudes = basemap(longitudes, latitudes)
    pcm = ax.scatter(longitudes, latitudes, c=hues, cmap="inferno", norm=mpl.colors.Normalize(vmin=0.0005, vmax=0.0025))
    return pcm, all_hues
    
def above_photic_limit(p:Profile, d:pd.DataFrame) -> float:
    return d[d["depth"] < p.photic_depth]

    
def below_photic_limit(p:Profile, d:pd.DataFrame) -> float:
    return d[d["depth"] >= p.photic_depth]




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

original_cmap = mpl.colormaps["PuBu_r"]
colors = original_cmap(np.arange(original_cmap.N))
colors[:, -1] = 0.7  # Set alpha
modified_cmap = ListedColormap(colors, "modified_cmap")
bmp = m.contourf(x, y, Z, cmap=modified_cmap)


m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])



pcm, hues = map_plot(all_valid_profiles, "bbp_minimum_despiked", ax[0], variable_limit=None, basemap=m)
#pcm, hues_above = map_plot(all_valid_profiles, "chlorophyll_corrected", ax[0], variable_limit=above_photic_limit, basemap=m)
#pcm, hues_below = map_plot(all_valid_profiles, "chlorophyll_corrected", ax[0], variable_limit=below_photic_limit, basemap=m)
ax[0].set_xlabel("Longitude", labelpad=15)
ax[0].set_ylabel("Latitude")

plt.suptitle(r"Average b$_{bp}$ in top 500 m of profile")
plt.colorbar(pcm, cax=ax[2], orientation="vertical")
ax[2].set_ylabel(r"mean b$_{bp}$ (m$^{-1}$)")
#ax[2].set_yticks([0.02, 0.05, 0.1, 0.2, 0.5], [0.02, 0.05, 0.1, 0.2, 0.5])
#ax[2].set_yticklabels([0.02, 0.05, 0.1, 0.2, 0.5])



ax[1].invert_xaxis()
plt.colorbar(bmp, cax=ax[1], orientation="horizontal")
ax[1].set_xlabel(r"Depth (m)")
xticks = ax[1].get_xticks()
ax[1].set_xticklabels([int(abs(tick)) for tick in xticks])











#plt.tight_layout()
plt.savefig("Louis/outputs/map_plot_bbp.png", dpi=300)
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