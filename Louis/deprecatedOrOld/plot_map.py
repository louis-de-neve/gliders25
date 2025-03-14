import cartopy.crs as ccrs
import cartopy.feature as cfeature

# plt.figure(figsize=(10, 6))
# ax = plt.axes(projection=ccrs.SouthPolarStereo())
# ax.set_extent([locations["longitude"].min() - 1, locations["longitude"].max() + 1,
#                locations["latitude"].min() - 1, locations["latitude"].max() + 1], crs=ccrs.PlateCarree())
# ax.add_feature(cfeature.LAND)
# ax.add_feature(cfeature.OCEAN)


# plt.title('Locations based on Longitude and Latitude')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.plot(locations["longitude"], locations["latitude"], transform=ccrs.PlateCarree())
# plt.show()