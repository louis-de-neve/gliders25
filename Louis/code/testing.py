from setup import import_split_and_make_transects

t, p = import_split_and_make_transects(use_cache=False,
                                       use_downcasts=True)
for profile in p:
    print(profile.data.columns)