from preprocessing.bbp.beta_to_bbp import beta_to_bbp
import numpy as np
from gsw import SA_from_SP, CT_from_t


def scatter_conversion_and_despiking(profiles:list, rerun=False) -> list:
    if not rerun:
        print("Despiking and converting scatter to bbp...")
    # interpolate temperature and salinity
    # calculate bbp using code from kate
    # apply 30 wide median, lowpass, 40 wide median and then 7 wide mean to bbp to get despiked

    # alternative method is the same as above, but then averaged with an average local minima (4x10wide rolling mean of the 30 wide minima)

    for i, profile in enumerate(profiles):
        beta = np.asarray(profile.data["scatter_650"])
        temp = np.asarray(profile.data["temperature_final"].interpolate())
        salinity = np.asarray(profile.data["salinity_final"].interpolate())   

        profile.data["bbp"] = beta_to_bbp(beta, temp, salinity)

        data_to_use = "bbp" if not rerun else "bbp_debubbled"

        temporary_df = profile.data.dropna(subset=[data_to_use]).copy()

        bbp = temporary_df[data_to_use]
        bbp_minima = bbp.rolling(window=7, min_periods=1, center=True).min()
        #for i in range(4):
        #   bbp_local_minima = bbp_local_minima.rolling(window=15, min_periods=1, center=True).mean()
        bbp_local_minima = bbp_minima.rolling(window=7, min_periods=1, center=True).max()


        if rerun:
            temporary_df["bbp_debubbled_despiked"] = bbp_local_minima

            profile.data = profile.data.merge(temporary_df, how="outer")


            profile.data["bbp_debubbled_despiked"] = profile.data["bbp_debubbled_despiked"].interpolate()
            spikes = profile.data["bbp_debubbled"] - profile.data["bbp_debubbled_despiked"]
            profile.data["bbp_debubbled_spikes"] = spikes
            spikes[spikes < 8.69388e-05] = 0
            profile.data["bbp_debubbled_spikes_denoised"] = spikes
        
        else:
            temporary_df["bbp_minimum_despiked"] = bbp_local_minima

            profile.data = profile.data.merge(temporary_df, how="outer")


            profile.data["bbp_minimum_despiked"] = profile.data["bbp_minimum_despiked"].interpolate()
            spikes = profile.data["bbp"] - profile.data["bbp_minimum_despiked"]
            profile.data["bbp_minimum_spikes"] = spikes
            spikes[spikes < 8.69388e-05] = 0
            profile.data["bbp_minimum_spikes_denoised"] = spikes


        # TODO ADD NOISE FILTERING FROM BRIGGS ET AL 2011
    return profiles