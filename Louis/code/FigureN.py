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
    t1_interior = lineplots(profiles, "#F00000FF", 3, 495, 546)
    t1_exterior = lineplots(profiles, "#0050F0FF", 3, 546, 565)
    t2_exterior = lineplots(profiles, "#43AFF3FF", 3, 565, 580)
    t2_interior = lineplots(profiles, "#F88737FF", 3, 580, 631)
    normal_points = lineplots(profiles, "#000000FF", 3, 631, ref_start)
    reference = lineplots(profiles, "#0EAB0EFF", 3, ref_start, ref_end)
    normal_points = lineplots(profiles, "#000000FF", 3, ref_end, 900)

    
    return normal_points, t1_interior, t1_exterior, t2_exterior, t2_interior, reference
    

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
additional_ax = fig.add_axes([0.05, 0.1, 0.43, 0.8])  # Additional map on the left
main_ax = fig.add_axes([0.52, 0.1, 0.4, 0.8])      # Main map on the right
side_ax = fig.add_axes([0.93, 0.1, 0.02, 0.8])   # [left, bottom, width, height]
axes = [main_ax, side_ax]

# Load data
dataset = xr.open_dataset('Louis/data/gebco_2024_n-55.0_s-65.0_w-40.0_e-32.0.nc', engine="netcdf4")

x = dataset.variables['lon']
y = np.asarray(dataset.variables['lat'])
Z = np.asarray(dataset.variables['elevation'])
m = Basemap(llcrnrlon=-40,llcrnrlat=-62.0,urcrnrlon=-34,urcrnrlat=-59.0,
            resolution='i',projection='merc',lon_0=-15.0,lat_0=55.0, ax=axes[0])



x,y = m(*np.meshgrid(x,y))
bmp = m.pcolormesh(x, y, Z, cmap=cmap, vmin=cmin, vmax=cmax)

contour = m.contour(x, y, Z, levels=[-3000], colors='#00000000', ax=main_ax)
vs = (contour.collections[0].get_paths()[0].vertices)
vs = vs[4970:8910]
contour_line = main_ax.plot(vs[:, 0], vs[:, 1], c="#575757", linestyle="dashed", label="3000 m isobath")




print(np.max(Z), np.min(Z))


m2 = Basemap(projection='merc', llcrnrlat=-68, urcrnrlat=-48, llcrnrlon=-64, urcrnrlon=-22,
             resolution='i', ax=additional_ax)
m2.drawcoastlines(linewidth=0.5)
dataset2 = xr.open_dataset('Louis/data/gebco_2024_n-47.0_s-68.0_w-64.0_e-22.0.nc', engine="netcdf4")

x2 = dataset2.variables['lon']
y2 = np.asarray(dataset2.variables['lat'])
Z2 = np.asarray(dataset2.variables['elevation'])

x2,y2 = m2(*np.meshgrid(x2,y2))



bmp2 = m2.pcolormesh(x2, y2, Z2, cmap=cmap, vmin=cmin, vmax=cmax)
m2.fillcontinents(color='white')



m2.plot([-34, -34, -40, -40, -34], [-62.0, -59.0, -59.0, -62.0, -62.0], color='black', linewidth=1, linestyle='dashed', latlon=True, label='Region enlarged below')
#additional_ax.legend(loc='lower left')
x2, y2 = -34, -61.5
xpt, ypt = m2(x2, y2)

# Add the text on top of the box
# additional_ax.text(xpt - 1600000, ypt - 400000, "Region enlarged", fontsize=10, color="red", fontweight="bold", ha="center", va="center",
#                    bbox=dict(facecolor='white', alpha=0.9, linewidth=0.5, pad=4))



# Add labels for the start and end profiles
start_profile = profiles[0]
end_profile = profiles[-1]

start_lon, start_lat = m(start_profile.start_location[0], start_profile.start_location[1])
end_lon, end_lat = m(end_profile.start_location[0], end_profile.start_location[1])
print(start_lon, start_lat)
# axes[0].text(start_lon, start_lat + 10000, "Start", fontsize=10, color="red", fontweight="bold", ha="center", va="center", 
#              bbox=dict(facecolor='white', alpha=0.9, linewidth=0.5, pad=4))
# axes[0].text(end_lon, end_lat - 10000, "End", fontsize=10, color="red", fontweight="bold", ha="center", va="center", 
#              bbox=dict(facecolor='white', alpha=0.9, linewidth=0.5, pad=4))

m.fillcontinents(color='grey')
m.drawparallels(np.arange(-65,-50,1), labels=[1,0,0,0], color='#000000A0')
m.drawmeridians(np.arange(-40, -30, 1), labels=[0,0,0,1], color='#000000A0')

m2.drawparallels(np.arange(-68,-48, 4), labels=[1,0,0,0], color='#000000A0')
m2.drawmeridians(np.arange(-66, -18, 8), labels=[0,0,0,1], color='#000000A0')



normal_points, t1_interior, t1_exterior, t2_exterior, t2_interior, reference = map_plot(profiles, axes[0], basemap=m)

# axes[0].legend([normal_points], ["track"])

axes[0].legend([normal_points, (t1_interior, t1_exterior), (t2_interior, t2_exterior), reference, contour_line[0]],
               ['Glider 631 path', 'Transect 1', 'Transect 2', 'Reference transect', '3000 m isobath'],
               loc='upper left', handler_map={tuple: HandlerTuple(ndivide=None)})


axes[0].set_xlabel("Longitude", labelpad=15)
axes[0].set_ylabel("Latitude")


additional_ax.set_xlabel("Longitude", labelpad=15)
additional_ax.set_ylabel("Latitude", labelpad=30)


#axes[1].invert_yaxis()
plt.colorbar(bmp, cax=axes[1], orientation="vertical")

axes[1].set_ylabel(r"Depth (m)")
xticks = axes[1].get_yticks()
axes[1].set_yticklabels([int(abs(tick)) for tick in xticks])


additional_ax.text(*m2(-63.6, -67), "WAP", size=12)
additional_ax.text(*m2(-37.5, -60.7), "DB", size=12)
additional_ax.text(*m2(-46, -61.5), "SOP", size=12)
additional_ax.text(*m2(-28.5, -60.8), "WF", size=12)
additional_ax.text(*m2(-60, -61.2), "SB", size=12)
additional_ax.text(*m2(-48.7, -53), "PF", size=12)
additional_ax.text(*m2(-56, -53), "SAF", size=12)
additional_ax.text(*m2(-53, -64.6), "ASF", size=12)
additional_ax.text(*m2(-37, -53.5), "South\nGeorgia", horizontalalignment='center', size=12)
additional_ax.text(*m2(-33.2, -66), "Weddell Sea", rotation=0, size=12)
additional_ax.text(*m2(-41, -63), "South Scotia Ridge", rotation=10, size=12)
additional_ax.text(*m2(-56, -58.5), "Scotia Sea", rotation=10, size=12)

# Open the Orsi Front data.xls file
wb = xlrd.open_workbook('Louis/data/southern_fronts/Orsi Front data.xls')
for sheetname in ["PF", "Boundary", "SAF"]:
    sheet = wb.sheet_by_name(sheetname)

# Read longitude and latitude columns (assuming columns 0 and 1, skipping header)
    lons = []
    lats = []
    for row_idx in range(1, sheet.nrows):
        lon = sheet.cell_value(row_idx, 0)
        lat = sheet.cell_value(row_idx, 1)
        if lon != '' and lat != '':
            lons.append(lon)
            lats.append(lat)

    # Plot on additional_ax using m2
    x_pf, y_pf = m2(lons, lats)
    additional_ax.plot(x_pf, y_pf, color='black', linewidth=2)

import scipy.io
wf_data = scipy.io.loadmat('Louis/data/southern_fronts/heywood/WF.mat')
xs = np.asarray(wf_data["lon_wf"][0])
ys = np.asarray(wf_data["lat_wf"][0])
xs = xs-360
x_wf, y_wf = m2(xs, ys)
additional_ax.plot(x_wf, y_wf, color='black', linewidth=2)


asf_data = scipy.io.loadmat('Louis/data/southern_fronts/heywood/ASF.mat')
xs = np.asarray(asf_data["lon_ASF"][0])
ys = np.asarray(asf_data["lat_ASF"][0])
xs = xs-360
x_asf, y_asf = m2(xs, ys)
additional_ax.plot(x_asf, y_asf, color='black', linestyle="--", linewidth=2)


# Optionally add to legend
# additional_ax.legend()


main_ax.text(*m(-36.9, -60.1), "Start", horizontalalignment='center', size=12)
main_ax.text(*m(-35, -60.2), "End", horizontalalignment='center', size=12)





#fig.tight_layout()
plt.savefig("Louis/figures/figureN.png", dpi=300)