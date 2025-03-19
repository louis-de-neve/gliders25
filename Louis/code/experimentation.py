from setup.setup import import_split_and_make_transects, Profile, Transect, two_dimensional_binning
from preprocessing.chlorophyll_corrections import scatter_and_chlorophyll_processing
from preprocessing.quenching.default import default_quenching_correction



transects, all_valid_profiles = import_split_and_make_transects(pre_processing_function=scatter_and_chlorophyll_processing,
                                                                use_cache=True,
                                                                quenching_method=default_quenching_correction,
                                                                use_downcasts=True,
                                                                use_supercache=True,
                                                                despiking_method="minimum")