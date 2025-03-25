from setup.setup import import_split_and_make_transects, Profile, Transect, two_dimensional_binning
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction
from plotting_functions import binned_plot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_cache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=False,
                                                                use_supercache=True,
                                                                despiking_method="minimum")
fig, axs = plt.subplots(2, 1, sharex=True, height_ratios=[4, 1])

t1 = transects[0].get_profiles()
t2 = transects[1].get_profiles()
t1 = t1[-10:]
t2 = t2[:10]

for i, profiles in enumerate([t1, t2]):

    up_day = [p for p in profiles if p.direction == "up" and not p.night]
    up_day_df = pd.concat([p.data for p in up_day])
    up_day_df["depth"] = up_day_df["depth"].round(0)
    up_day_df = up_day_df[up_day_df["depth"] > 1]

    up_day_df.groupby("depth")["chlorophyll_corrected"].mean()
    up = up_day_df.groupby("depth")["bbp"].mean().values
    depths = up_day_df.groupby("depth")["bbp_minimum_spikes"].mean().index
    c = up_day_df.groupby("depth")["chlorophyll_corrected"].mean().values

    chlorophyll_max = max(c)
    bbp_above_point = [sum(up[:i]) for i in range(len(up))]

    #up = up / max(up)
    c = c/max(c)   
    #bbp_above_point = bbp_above_point / max(bbp_above_point)

    #sns.lineplot(data=up_day_df, x="depth", y="chlorophyll_corrected", label="Upcasts_corrected")
    #sns.lineplot(data=down_day_df, x="depth", y="chlorophyll_corrected", label="Downcasts_corrected")
    axs[1].plot(depths, up, label=f"Transect {i}")
    #plt.plot(depths, c, label=f"Chlorophyll{i}")
    axs[0].plot(depths, bbp_above_point, label=f"Transect {i}")






axs[0].set_ylabel("Total BBP above point")
axs[1].set_ylabel("BBP")
axs[1].set_xlabel("Depth (m)")
plt.legend()
plt.xlim(-5, 1000)
#axs[1].set_ylim(0, 1)
plt.show()