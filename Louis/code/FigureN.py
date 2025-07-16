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
from matplotlib.legend_handler import HandlerTuple
from matplotlib.patches import FancyBboxPatch

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


def map_plot(profiles:list[Profile], ax, basemap=None) -> None:

    profiles.pop(576)
    #profiles = [p for p in profiles if p.direction == "up"]
    
    def lineplots(profiles, color, width, start, stop):
        normal_profiles = [p for p in profiles if p.index < stop and p.index >= start]
        lon, lat = basemap([p.start_location[0] for p in normal_profiles],
                           [p.start_location[1] for p in normal_profiles])
        plot_obj, = ax.plot(lon, lat, color=color, linewidth=width, zorder=2)
        return plot_obj

    ref_start = 710
    ref_end = 760



    normal_points = lineplots(profiles, "#000000FF", 3, 0, 495)
    t1_interior = lineplots(profiles, "#F00000FF", 3, 495, 550)
    t1_exterior = lineplots(profiles, "#0050F0FF", 3, 550, 565)
    t2_exterior = lineplots(profiles, "#43AFF3FF", 3, 565, 580)
    t2_interior = lineplots(profiles, "#F88737FF", 3, 580, 631)
    normal_points = lineplots(profiles, "#000000FF", 3, 631, ref_start)
    reference = lineplots(profiles, "#0EAB0EFF", 3, ref_start, ref_end)
    normal_points = lineplots(profiles, "#000000FF", 3, ref_end, 900)

    
    return normal_points, t1_interior, t1_exterior, t2_exterior, t2_interior, reference
    




#fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
fig = plt.figure(figsize=(12, 6))  # Landscape orientation
additional_ax = fig.add_axes([0.03, 0.1, 0.4, 0.8])  # Additional map on the right
main_ax = fig.add_axes([0.48, 0.1, 0.4, 0.8])      # Main map on the left
side_ax = fig.add_axes([0.92, 0.1, 0.02, 0.8])     # Colorbar next to main map
#side_ax = fig.add_axes([0.08, 0.05, 0.02, 0.42])  # [left, bottom, width, height]
axes = [main_ax, side_ax]

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





m2 = Basemap(projection='spstere',boundinglat=-50,lon_0=180, llcrnrlat=-60, resolution='i', ax=additional_ax)
m2.etopo()

m2.plot([-34, -34, -40, -40, -34], [-62.0, -59.0, -59.0, -62.0, -62.0], color='red', linewidth=2, latlon=True, label='Region enlarged below')
#additional_ax.legend(loc='lower left')
x2, y2 = -34, -61.5
xpt, ypt = m2(x2, y2)

# Add the text on top of the box
additional_ax.text(xpt - 1600000, ypt - 400000, "Region enlarged", fontsize=10, color="red", fontweight="bold", ha="center", va="center",
                   bbox=dict(facecolor='white', alpha=0.9, linewidth=0.5, pad=4))



# Add labels for the start and end profiles
start_profile = profiles[0]
end_profile = profiles[-1]

start_lon, start_lat = m(start_profile.start_location[0], start_profile.start_location[1])
end_lon, end_lat = m(end_profile.start_location[0], end_profile.start_location[1])
print(start_lon, start_lat)
axes[0].text(start_lon, start_lat + 10000, "Start", fontsize=10, color="red", fontweight="bold", ha="center", va="center", 
             bbox=dict(facecolor='white', alpha=0.9, linewidth=0.5, pad=4))
axes[0].text(end_lon, end_lat - 10000, "End", fontsize=10, color="red", fontweight="bold", ha="center", va="center", 
             bbox=dict(facecolor='white', alpha=0.9, linewidth=0.5, pad=4))

m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])



normal_points, t1_interior, t1_exterior, t2_exterior, t2_interior, reference = map_plot(profiles, axes[0], basemap=m)

# axes[0].legend([normal_points], ["track"])

axes[0].legend([normal_points, (t1_interior, t1_exterior), (t2_interior, t2_exterior), reference],
               ['Glider 631 path', 'Transect 1', 'Transect 2', 'Reference transect'],
               loc='upper left', handler_map={tuple: HandlerTuple(ndivide=None)})


axes[0].set_xlabel("Longitude", labelpad=15)
axes[0].set_ylabel("Latitude")


#axes[1].invert_yaxis()
plt.colorbar(bmp, cax=axes[1], orientation="vertical")
axes[1].set_ylabel(r"Depth (m)")
xticks = axes[1].get_yticks()
axes[1].set_yticklabels([int(abs(tick)) for tick in xticks])



#fig.tight_layout()
plt.savefig("Louis/figures/figureN.png", dpi=300)