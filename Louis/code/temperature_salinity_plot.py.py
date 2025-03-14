import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects
from code.plotting_functions import temp_salinity_plot
from Louis.code.preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing

transects, all_valid_profiles = import_split_and_make_transects(parameters="all", pre_processing_function=scatter_and_chlorophyll_processing)
    
#all transect temp/salinity plot:
fig, axs = plt.subplots(2, 5, figsize=(30, 10), sharey=True)
axs = axs.flatten()

for transect, ax in zip(transects, axs):
    ax.set_title(transect.name)
    pcm = temp_salinity_plot(transect.get_profiles(), ax)

cbar_ax = fig.add_axes([0.15, 0.03, 0.7, 0.02])
plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
cbar_ax.set_xlabel("Depth (m)")

plt.savefig("Louis/outputs/TS_all_transects.png", dpi=300)
plt.show()