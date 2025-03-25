import matplotlib.pyplot as plt
from setup.setup import import_split_and_make_transects, Transect, Profile
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction
from plotting_functions import binned_plot
import matplotlib as mpl
from matplotlib import MatplotlibDeprecationWarning
import warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore",category=MatplotlibDeprecationWarning)


transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_supercache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=False,
                                                                despiking_method="minimum")


tA = all_valid_profiles[2:47]
tA.pop(5)
tA = [p.data for p in tA]

tB = [p.data for p in all_valid_profiles[64:105]]
2

tA = pd.concat(tA).dropna(subset=["bbp_minimum_spikes"])
tB = pd.concat(tB).dropna(subset=["bbp_minimum_spikes"])

tA["depth"] = tA["depth"].round(0)
tB["depth"] = tB["depth"].round(0)

tAspikes = tA.groupby("depth")["bbp_minimum_spikes"].mean()
tBspikes = tB.groupby("depth")["bbp_minimum_spikes"].mean()

tAsum = [sum(tAspikes[:i]) for i in range(len(tAspikes))]
tBsum = [sum(tBspikes[:i]) for i in range(len(tBspikes))]

plt.plot(tAsum, label="Transect A")
plt.plot(tBsum, label="Transect B")
plt.legend()
plt.show()