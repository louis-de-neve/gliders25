widths = [4, 6, 8, 10, 12, 14, 16]
result_dict = {n: [] for n in widths}
print(result_dict)


result_dict[8].append(5.83)

print(result_dict)




# from setup import import_split_and_make_transects, Profile, Transect
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import matplotlib as mpl
# from matplotlib.axes import Axes
# from plotting_functions import new_binned_plot
# transects, profiles = import_split_and_make_transects(use_cache=True,
#                                                       use_downcasts=True,)

# # from preprocessing.chlorophyll.default_quenching import default_quenching_correction
# # profiles = default_quenching_correction(profiles)
# fig, axs = plt.subplots(ncols=2, figsize=(10, 10))

# profiles.pop(576)
# profiles[537].end_time = profiles[538].end_time # PATCH HOLE IN DATA
# profiles[540].start_time = profiles[539].start_time
# profiles.pop(539)
# profiles.pop(538)



# profiles1 = profiles[494:562]
# profiles2 = profiles[562:625]

# interior = profiles1[:-20] + profiles2[15:]
# exterior = profiles1[-20:] + profiles2[:15]



# print(profiles[0].index, profiles[-1].index)

# az_depths = [-p.active_zone for p in profiles]

# # AXIS 0

# my_cmap = mpl.colormaps["viridis"].copy()
# my_cmap.set_extremes(over=(0,0,0), under=(1,1,1))
# my_norm = mpl.colors.LogNorm(vmin=0.015, vmax=2.5, clip=True)

# pcm = new_binned_plot(interior, axs[0], "chlorophyll_corrected", 3, 800, cmap=my_cmap, norm=my_norm)
# pcm = new_binned_plot(exterior, axs[1], "chlorophyll_corrected", 3, 800, cmap=my_cmap, norm=my_norm)
# plt.show()
