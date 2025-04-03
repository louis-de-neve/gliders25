import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress
from scipy.optimize import curve_fit
import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)

def bubble_correction(profiles:list) -> list:
    print("Applying bubble correction...")
    downcasts = [p for p in profiles if p.direction == "down"]
    upcasts = [p for p in profiles if p.direction == "up"]
    upcast_data = [p.apply_binning_to_parameter("bbp_minimum_despiked", 1, 1000) for p in upcasts]
    upcast_times_dict = {p.start_time : i for i, p in enumerate(upcasts)}
    ylocs = [0, 10, 20, 30, 50, 100, 999]
    
    def piecewise_function(xs, *yvals):
        section = np.zeros_like(xs)
        for i, xlim in enumerate(ylocs[:-1]):
            section = section + np.asarray([yvals[i] + (yvals[i+1] - yvals[i]) * (x - xlim) / (ylocs[i+1] - xlim) if (x >= xlim) and (x < ylocs[i+1]) else 0 for x in xs])

        return section

    for i, downcast in enumerate(downcasts):
        st = downcast.start_time
        relative_times = {abs(st - t): i for t, i in upcast_times_dict.items()}
        closest_times = [abs(st - t) for t in upcast_times_dict.keys()]
        closest_times.sort()
        closest_upcasts_data = [upcast_data[relative_times[t]] for t in closest_times[:6]]
        
        mean_of_closests_upcasts = np.nanmean(closest_upcasts_data, axis=0)
        
        
        downcast_data = np.asarray(downcast.apply_binning_to_parameter("bbp_minimum_despiked", 1, 1000))
        downcast_data = np.nan_to_num(downcast_data, nan=0)
               

        difference = (downcast_data - mean_of_closests_upcasts)
        difference = np.nan_to_num(difference, nan=0)
        
        d2 = np.maximum(difference, 0)

        popt, pcov = curve_fit(piecewise_function, np.arange(1000), difference, p0=[d2[i] for i in ylocs], bounds=(0, np.inf))
        adjustment_test = piecewise_function(np.arange(1000), *popt)
        profiles[int(downcast.index - 1)].data["bbp_debubbled"] = downcast.data["bbp_minimum_despiked"] - np.interp(downcast.data["depth"], np.arange(1000), adjustment_test)
        

    for p in profiles:
        if "bbp_debubbled" not in p.data.columns:
            p.data["bbp_debubbled"] = p.data["bbp_minimum_despiked"]

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

