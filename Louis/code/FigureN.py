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

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)


def map_plot(profiles:list[Profile], ax, basemap=None) -> None:

    profiles.pop(576)
    

    for p in profiles:
        c = "#21D302FF"
        if p.index < 635 and p.index >= 490:
            c = "#F00000FF" # Profiles used in Figures I and M
        
        lon, lat = basemap(p.start_location[0], p.start_location[1])

        if p.index == 560:
            z1 = ax.scatter(lon, lat, c=c,
                            marker="o",
                            s=80,
                            edgecolor="black",
                            linewidth=0.3,
                            alpha=0.8,)
        else:
            z0 = ax.scatter(lon, lat, c=c,
                            marker="o",
                            s=80,
                            edgecolor="black",
                            linewidth=0.3,
                            alpha=0.8)
        
        
        
        if p.index < 599 and p.index >= 545:    
            c = "#00DEF2FF" # Profiles used in Figures E and F
            z2 = ax.scatter(lon, lat, c=c,
                                marker="o",
                                s=60,
                                edgecolor="#F00000FF",
                                linewidth=1,
                                alpha=0.9,)

    return z0, z1, z2
    




#fig, ax = plt.subplots(2, 1, figsize=(6,6), height_ratios=[1, 0.05])
fig = plt.figure(figsize=(8,8))
main_ax = fig.add_axes([0.1, 0.14, 0.8, 0.82])  # [left, bottom, width, height]
side_ax = fig.add_axes([0.1, 0.06, 0.8, 0.02])  # [left, bottom, width, height]
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
colors[:, -1] = 0.8  # Set alpha
modified_cmap = ListedColormap(colors, "modified_cmap")
bmp = m.contourf(x, y, Z, cmap=modified_cmap)

# Add labels for the start and end profiles
start_profile = profiles[0]
end_profile = profiles[-1]

start_lon, start_lat = m(start_profile.start_location[0], start_profile.start_location[1])
end_lon, end_lat = m(end_profile.start_location[0], end_profile.start_location[1])
print(start_lon, start_lat)
axes[0].text(start_lon, start_lat + 10000, "Start", fontsize=10, color="red", fontweight="bold", ha="center", va="center")
axes[0].text(end_lon, end_lat - 10000, "End", fontsize=10, color="red", fontweight="bold", ha="center", va="center")

m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])



z0, z1, z2 = map_plot(profiles, axes[0], basemap=m)


axes[0].legend()



axes[0].set_xlabel("Longitude", labelpad=15)
axes[0].set_ylabel("Latitude")


axes[1].invert_xaxis()
plt.colorbar(bmp, cax=axes[1], orientation="horizontal")
axes[1].set_xlabel(r"Depth (m)")
xticks = axes[1].get_xticks()
axes[1].set_xticklabels([int(abs(tick)) for tick in xticks])


axes[0].legend([z0, z1, (z1, z2)], ['Glider 631 Track', 'Transect 1', 'Transect 2 (Subset of Transect 1)'],
               loc='upper left')

#fig.tight_layout()
plt.savefig("Louis/figures/figureN.png", dpi=300)