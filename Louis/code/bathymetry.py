import netCDF4
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

# Load data
dataset = netCDF4.Dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc')
print(np.shape(dataset.variables["elevation"]))

# Extract variables
x = dataset.variables['lon']
y = np.asarray(dataset.variables['lat'])[::-1]
Z = np.asarray(dataset.variables['elevation'])



m = Basemap(llcrnrlon=-42,llcrnrlat=-65.0,urcrnrlon=-30,urcrnrlat=-53.0,
            resolution='i',projection='stere',lon_0=-15.0,lat_0=55.0)

x,y = m(*np.meshgrid(x,y))

m.contourf(x, y, np.flipud(Z))
m.fillcontinents(color='grey')
m.drawparallels(np.arange(10,70,10), labels=[1,0,0,0])
m.drawmeridians(np.arange(-80, 5, 10), labels=[0,0,0,1])
plt.show()