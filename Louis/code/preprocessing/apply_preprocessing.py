from preprocessing.bbp.scatter_despiking import scatter_conversion_and_despiking
from preprocessing.bbp.bubble_correction import bubble_correction
from preprocessing.chlorophyll.deep_chlorophyll_correction import deep_chlorophyll_correction
from preprocessing.chlorophyll.default_quenching import default_quenching_correction
from preprocessing.depth_calculations.mld import MLD_calculation
from preprocessing.depth_calculations.photic import photic_calculation



def scatter_and_chlorophyll_processing(profiles:list, use_downcasts:bool) -> list:
    functions_to_apply = [
        scatter_conversion_and_despiking,
        bubble_correction,
        MLD_calculation,
        deep_chlorophyll_correction,
        photic_calculation,
        default_quenching_correction,
    ]
    
    if not use_downcasts:
        functions_to_apply.pop(1) # dont bubble correct if theyre ignored
    
    for function in functions_to_apply:
        profiles = function(profiles)

    return profiles
