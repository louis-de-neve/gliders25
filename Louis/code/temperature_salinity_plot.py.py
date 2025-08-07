import matplotlib.pyplot as plt
from setup import import_split_and_make_transects
from plotting_functions import temp_salinity_plot
from preprocessing.apply_preprocessing import scatter_and_chlorophyll_processing

transects, profiles = import_split_and_make_transects(use_cache=True,
                                                                use_downcasts=True,)


profiles.pop(576)
profiles = [p for p in profiles if p.index != 614]

profiles1 = [p for p in profiles if p.index >= 495 and p.index < 565]
profiles2 = [p for p in profiles if p.index >= 565 and p.index < 631]

interior1 = [p for p in profiles if p.index >= 495 and p.index < 550]
interior2 = [p for p in profiles if p.index >= 580 and p.index < 631]
exterior1 = [p for p in profiles if p.index >= 550 and p.index < 565]
exterior2 = [p for p in profiles if p.index >= 565 and p.index < 580]
exterior = exterior1 + exterior2
interior = interior1 + interior2

ref = [p for p in profiles if p.index >= 710 and p.index < 760]


#all transect temp/salinity plot:
fig = plt.figure(figsize=(12, 4))

ax1 = fig.add_axes([0.1, 0.22, 0.25, 0.7])
ax2 = fig.add_axes([0.4, 0.22, 0.25, 0.7], sharey=ax1)
ax3 = fig.add_axes([0.7, 0.22, 0.25, 0.7], sharey=ax1)

axs = [ax1, ax2, ax3]

for transect, ax in zip([interior, exterior, ref], axs):
    #ax.set_title(transect.name)
    pcm = temp_salinity_plot(transect, ax)

ax1.set_title("Interior")
ax2.set_title("Edge")
ax3.set_title("Reference")



cbar_ax = fig.add_axes([0.15, 0.11, 0.7, 0.02])
plt.colorbar(pcm, cax=cbar_ax, orientation="horizontal")
cbar_ax.set_xlabel("Depth (m)")
plt.savefig("Louis/outputs/TS_all_transects.png", dpi=300)