from setup import import_split_and_make_transects, Profile, Transect
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import copy
from scipy.stats import linregress
from preprocessing.bbp.bubble_correction import bubble_correction
transects, profiles = import_split_and_make_transects(use_cache=True,
                                                      use_downcasts=True,)

profiles.pop(243)

widths = [16, 8, 10, 12, 14, 6]
result_dict = {w: [] for w in widths}
result_dict_top_100 = {w: [] for w in widths}

for n in [520]:
    profiles_temp1 = copy.deepcopy(profiles[n:(n+70)])
    del profiles
    for i, p in enumerate(profiles_temp1):
        p.index = i
        if "bbp_debubbled_despiked" in p.data.columns:
            p.data.drop(columns=["bbp_debubbled_despiked"], inplace=True)

    for width in widths:
        print(f"computing width: {width} at {n}")
        p_temp = copy.deepcopy(profiles_temp1)

        profiles_temp = bubble_correction(p_temp, width)
        profiles_temp = profiles_temp[10:-10]

        up = [p.data for p in profiles_temp if p.direction == "up"]
        down  = [p.data for p in profiles_temp if p.direction == "down"]
        del profiles_temp

        up = pd.concat(up).dropna(subset=["bbp_minimum_despiked"])
        down = pd.concat(down).dropna(subset=["bbp_minimum_despiked"])
        up["depth"] = up["depth"].round(0)
        down["depth"] = down["depth"].round(0)
        up_original = up.groupby("depth")["bbp_minimum_despiked"].mean()
        down_original = down.groupby("depth")["bbp_minimum_despiked"].mean()
        down_new = down.groupby("depth")["bbp_debubbled_despiked"].mean()
        old_diff = down_original - up_original
        new_diff = down_new - up_original
        old_diff.pop(1)
        old_diff.pop(0) # ignore top 1m (0 and 1m)
        new_diff.pop(1)
        new_diff.pop(0)
        new_diff = abs(new_diff)
        old_diff = abs(old_diff)
        old_avg = np.mean(old_diff)
        new_avg = np.mean(new_diff)
        old_avg_100 = np.mean(list(old_diff)[:98])
        new_avg_100 = np.mean(list(new_diff)[:98])
        improvement100 = old_avg_100 / new_avg_100
        improvement = old_avg / new_avg

        result_dict[width].append(improvement)
        result_dict_top_100[width].append(improvement100)

    with open(f"Louis/cache/analysis{n}.pkl", "wb") as f:
        pd.to_pickle({"dict": result_dict, "dict100": result_dict_top_100}, f)

