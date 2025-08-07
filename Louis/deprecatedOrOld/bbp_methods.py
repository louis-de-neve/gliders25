import matplotlib.pyplot as plt
from setup import import_split_and_make_transects, Transect, Profile
from preprocessing.apply_preprocessing import scatter_and_chlorophyll_processing
from preprocessing.chlorophyll.default_quenching import default_quenching_correction
from plotting_functions import binned_plot
import matplotlib as mpl
from matplotlib import MatplotlibDeprecationWarning
import warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore",category=MatplotlibDeprecationWarning)


transects, all_valid_profiles = import_split_and_make_transects(use_cache=True,
                                                                use_downcasts=True,)
profiles = all_valid_profiles[1:211]
up = [p.data for p in profiles if p.direction == "up"]
down  = [p.data for p in profiles if p.direction == "down"]



up = pd.concat(up).dropna(subset=["bbp_minimum_despiked"])
down = pd.concat(down).dropna(subset=["bbp_minimum_despiked"])

up["depth"] = up["depth"].round(0)
down["depth"] = down["depth"].round(0)

up_original = up.groupby("depth")["bbp_minimum_despiked"].mean()
down_original = down.groupby("depth")["bbp_debubbled_old"].mean()
#down_original = down.groupby("depth")["bbp_minimum_despiked"].mean()
down_new = down.groupby("depth")["bbp_debubbled_despiked"].mean()

old_diff = down_original - up_original
new_diff = down_new - up_original
old_diff.pop(0)
old_diff.pop(1) # ignore top 1m (0 and 1m)
new_diff.pop(0)
new_diff.pop(1)

old_avg = np.mean(old_diff)
new_avg = np.mean(new_diff)

old_avg_100 = np.mean(old_diff[:100])
new_avg_100 = np.mean(new_diff[:100])


plt.plot(old_diff, label="Debubbling applied to despiked data\n mean = {:.2e}, top 100 mean: {:.2e}".format(old_avg, old_avg_100))
plt.plot(new_diff, label='Debubbling applied to raw data, then despiked\n mean = {:.2e}, top 100 mean: {:.2e}'.format(new_avg, new_avg_100))
plt.xlabel("Depth (m)")
plt.ylabel(r"$\Delta b_{bp}$ ($m^{-1}$)")
plt.title("Difference between down and up casts")
plt.savefig("Louis/outputs/bbp_method.png", dpi=300)
plt.legend()
plt.show()