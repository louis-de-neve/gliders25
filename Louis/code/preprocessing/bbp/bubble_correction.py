import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
from scipy.optimize import curve_fit
import warnings
from tqdm import tqdm
from preprocessing.bbp.scatter_despiking import scatter_conversion_and_despiking
warnings.simplefilter("ignore", category=RuntimeWarning)

def bubble_correction(profiles:list, width:int=10) -> list:
    #print("Applying bubble correction...")
    downcasts = [p for p in profiles if p.direction == "down"]
    upcasts = [p for p in profiles if p.direction == "up"]
    upcast_data = [p.apply_binning_to_parameter("bbp_minimum_despiked", 1, 1000) for p in upcasts]
    upcast_times_dict = {p.end_time : i for i, p in enumerate(upcasts)}
    ylocs = [0, 10, 20, 30, 50, 80, 120, 160, 990]
    ylocs = np.append(np.arange(0, 170, width), 990)
    
    def piecewise_function(xs, *yvals):
        section = np.zeros_like(xs)
        for j, xlim in enumerate(ylocs[:-1]):
            section = section + np.asarray([yvals[j] + (yvals[j+1] - yvals[j]) * (x - xlim) / (ylocs[j+1] - xlim) if (x >= xlim) and (x < ylocs[j+1]) else 0 for x in xs])
        return section

    indexes = [p.index for p in profiles]
    comparisons = 6

    for i, downcast in tqdm(enumerate(downcasts)):
        profile_list_index = int(indexes.index(downcast.index))
        st = downcast.start_time
        relative_times = {abs(st - t): i for t, i in upcast_times_dict.items()}
        closest_times = [abs(st - t) for t in upcast_times_dict.keys()]
        closest_times.sort()
        closest_upcasts_data = [upcast_data[relative_times[t]] for t in closest_times[:comparisons]]
        
        mean_of_closests_upcasts = np.nanmean(closest_upcasts_data, axis=0)
        
        
        downcast_data = np.asarray(downcast.apply_binning_to_parameter("bbp_minimum_despiked", 1, 1000))
        downcast_data = np.nan_to_num(downcast_data, nan=0)
               

        difference = (downcast_data - mean_of_closests_upcasts)
        difference = np.nan_to_num(difference, nan=0)
        
        d2 = np.maximum(difference, 0)
        p0 = [d2[i] for i in ylocs]


        popt, pcov = curve_fit(piecewise_function, np.arange(1000), difference, p0=p0, bounds=(0, np.inf))
        bubble_correction_adjustment = piecewise_function(np.arange(1000), *popt)
        bubble_correction_adjustment = difference
        # if i == 25:
        #     plt.plot(difference, color="black")
        #     plt.plot(bubble_correction_adjustment, color="red")
        #     plt.show()
        raw_debubbled = downcast.data["bbp"] - np.interp(downcast.data["depth"], np.arange(1000), bubble_correction_adjustment)
        profiles[profile_list_index].data["bbp_debubbled"] = raw_debubbled
        profiles[profile_list_index].data["bbp_debubbled_old"] = downcast.data["bbp_minimum_despiked"] - np.interp(downcast.data["depth"], np.arange(1000), bubble_correction_adjustment)
    

    for p in profiles:
        if "bbp_debubbled" not in p.data.columns:
            p.data["bbp_debubbled"] = p.data["bbp"]
        if "bbp_debubbled_old" not in p.data.columns:
            p.data["bbp_debubbled_old"] = p.data["bbp_minimum_despiked"]

    profiles = scatter_conversion_and_despiking(profiles, rerun=True)
    return profiles
        
        # OLD METHOD
        # slope1, intercept1 = linregress(np.arange(100, 1000), difference[100:1000])[:2] # main trend 
        # slope2, intercept2 = linregress(np.arange(10, 100), difference[10:100])[:2] # top 100m trend
        # slope3, intercept3 = linregress(np.arange(10), difference[:10])[:2] # top 10m trend
        # if not( np.isnan(slope1) or np.isnan(slope2) or np.isnan(slope3)):

        #     adj1 = slope1 * np.arange(1000) + intercept1
        #     adj2 = slope2 * np.arange(100) + intercept2
        #     adj3 = slope3 * np.arange(10) + intercept3
        #     adj3 = np.maximum(adj3, adj2[:10]) # remove negative values
        #     adj2 = np.maximum(adj2, adj1[:100])
        #     adjustment = np.concatenate([adj3, adj2[10:], adj1[100:]])
        #     adjustment = np.maximum(adjustment, 0)
        

        #     new_downcast_data = downcast_data - adjustment




        # if downcast.index in [49.0, 61.0]:
        #     print("Slope1:", slope1)
        #     print("Slope2:", slope2)
        #     print("Slope3:", slope3)
        #     # plt.plot(profiles[int(downcast.index - 1)].data["bbp_debubbled"], color="red")
        #     # plt.plot(downcast.data["bbp_minimum_despiked"], color="blue")
        #     # plt.show()
        #     #plt.plot(new_downcast_data, color="black")
            
        #     plt.plot(downcast_data, color="green")
        #     plt.plot(adjustment, color="red")
        #     plt.plot(mean_of_closests_upcasts, color="blue")
        #     plt.plot(difference, color="orange")
        #     plt.plot(adjustment_test, color="purple")
        #     #plt.plot(slope1 * np.arange(500) + intercept1, color="orange")
        #     #plt.plot(slope2 * np.arange(50) + intercept2, color="purple")
        #     #plt.plot(slope3 * np.arange(5) + intercept3, color="limegreen")
        #     plt.show()

