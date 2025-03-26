import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

def bubble_correction(profiles:list) -> list:
    print("Applying bubble correction...")
    
    downcasts = [p for p in profiles if p.direction == "down"]
    upcasts = [p for p in profiles if p.direction == "up"]
    upcast_data = [p.apply_binning_to_parameter("bbp_minimum_despiked", 2, 1000) for p in upcasts]
    upcast_times_dict = {p.start_time : i for i, p in enumerate(upcasts)}
    
    for i, downcast in enumerate(downcasts):
        st = downcast.start_time
        relative_times = {abs(st - t): i for t, i in upcast_times_dict.items()}
        closest_times = [abs(st - t) for t in upcast_times_dict.keys()]
        closest_times.sort()
        closest_upcasts_data = [upcast_data[relative_times[t]] for t in closest_times[:5]]
        
        mean_of_closests_upcasts = np.mean(closest_upcasts_data, axis=0)
        #mean_of_closests_upcasts_sample = mean_of_closests_upcasts[:50] # top 100m
        
        downcast_data = np.asarray(downcast.apply_binning_to_parameter("bbp_minimum_despiked", 2, 1000))
        #downcast_data_sample = downcast_data[:50] # top 100m
        #slope = linregress(downcast_data_sample, mean_of_closests_upcasts_sample)[0]

        #downcast_data2 = [a*slope for a in downcast_data_sample] + list(downcast_data[50:])

        difference = (downcast_data - mean_of_closests_upcasts)
        #difference = [np.nan if i < 50 else a for i, a in enumerate(difference)]
        
        slope1, intercept1 = linregress(np.arange(450), difference[50:])[:2]
        slope2, intercept2 = linregress(np.arange(50), difference[:50])[:2]

        if i in [17, 18]:
            plt.plot(downcast_data, color="green")
            plt.plot(mean_of_closests_upcasts, color="blue")
            plt.plot(difference, color="red")
            plt.plot(slope1 * np.arange(500) + intercept1, color="orange")
            plt.plot(slope2 * np.arange(50) + intercept2, color="purple")
            plt.show()

            
    # TODO :
    # - ignore the top 1m
    # - find the difference between the slopes
    # - subtract the difference between the slopes from the downcast data
    # - compare 


    for profile in profiles:




        pass

    sample = profiles[17:19]
    for profile in sample:
        c1 = "red" if profile.direction == "up" else "blue"
        c2 = "orange" if profile.direction == "up" else "cyan"

        plt.plot(profile.data["depth"], profile.data["bbp_minimum_despiked"], color=c1)
        plt.plot(profile.data["depth"], profile.data["bbp"], color=c2)
        plt.plot()        
    
    plt.show()
    #plt.savefig("Louis/outputs/bubble_correction.png", dpi=300)
    exit()
    return profiles

