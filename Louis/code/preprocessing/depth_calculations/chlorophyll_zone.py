import pandas as pd
import numpy as np

def chlorophyll_zone(profiles:list) -> list:
    """
    This function calculates the depth of the active zone for each profile based on chlorophyll data.
    The active zone is defined as the depth at which chlorophyll concentration is less than 1% of the 95th percentile
    of chlorophyll concentration in the top 100 meters of the profile.
    """
    print("Calculating chlorophyll zones...")
    # Calculate the chlorophyll zone for each profile
    for p in profiles:
        bin_size = 2
        c_data = p.apply_binning_to_parameter("chlorophyll_corrected", bin_size, 1000)
        
        chlorophyll95 = pd.Series(c_data[:50]).quantile(0.95)
        chlorophyll95 = 2 if chlorophyll95 < 2 else chlorophyll95

        c_data = pd.Series(c_data)

        c_data_smoothed = list(c_data.rolling(3, min_periods=1).mean())

        for i, value in enumerate(c_data_smoothed):
            if value < 0.01 * chlorophyll95:
                break
        if i * bin_size > 500:
            i = 0
        p.active_zone = i * bin_size if i !=0 else np.nan

    return profiles