import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Profile, Transect
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
from matplotlib.colors import ListedColormap

def transect_map(transects:list[Transect], profiles:list[Profile], m) -> None:
    for t in transects:
        x, y = tuple(zip(t.start_location, t.finish_location))
        x, y = m(x, y)
        plt.plot(x, y, label=t.name)
    for i, p in enumerate(profiles):
        x, y = tuple(zip(p.start_location, p.end_location))
        x, y = m(x, y)
        plt.scatter(x, y, color="black", alpha=0.1)
        plt.text(x[0], y[0], i, fontsize=5)
    plt.legend()



dataset = xr.open_dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc', engine="netcdf4")

x = dataset.variables['lon']
y = np.asarray(dataset.variables['lat'])
Z = np.asarray(dataset.variables['elevation'])
m = Basemap(llcrnrlon=-40,llcrnrlat=-62.0,urcrnrlon=-34,urcrnrlat=-59.0,
            resolution='i',projection='stere',lon_0=-15.0,lat_0=55.0)
x,y = m(*np.meshgrid(x,y))

original_cmap = mpl.colormaps["PuBu_r"]
colors = original_cmap(np.arange(original_cmap.N))
colors[:, -1] = 0.7  # Set alpha
modified_cmap = ListedColormap(colors, "modified_cmap")
bmp = m.contourf(x, y, Z, cmap=modified_cmap)


m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0])
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1])




transects, all_valid_profiles = import_split_and_make_transects(use_supercache=True)
profiles = all_valid_profiles[2:47] + all_valid_profiles[64:105]
transect_map(transects, profiles, m)
plt.savefig("Louis/outputs/transect_map.png", dpi=300)
plt.show()