# gliders25
Masters Project on Gliders


# Code Log
### pre 11th Feb
created methods in main.py for handling mat data by splitting into up and down casts
```python
def import_data_from_mat_file

def split_dataframe_by_cast

def sanitise_casts
```
### 11th Feb
created methods in main.py for displaying downcasts:
```python
class Cast

def two_dimensional_binning

def binned_plot
``` 

### 12th Feb

Created transect indices`transect_information.py`. denoting the start and end indexes of the transects A through J. `all_transect_indexes`

Manually checked each transect to highlight  problematic up/down casts. `transect_information.py``transect_problems`

removed problematic down/upcasts and fixed where signal processing had offset profiles

started working on a method to convert downcast numbers to distances/times

(i then realised there is a field in the data called `profile index` that makes almost all my work to date redundant 😠)

### 13th Feb

rewrote the code for splitting up profiles to use the built-in indices - the profile numbers (832) now matches those in Alex's paper.

Merged non-integer profile indices relating to profiles near the surface

generated a [transect map](Louis/outputs/transect_map.png)

shifted sections of setup code into [setup.py](setup.py)

deprecated `transect_information.py`

### 18th Feb

rewrote the bbp correction code into python

# TO DO

write code to identify night/day

despike the beta data and convert to bbp using new script

depth correction for >300m - 95% and then convert -ve to zero

take average of the night before and after as the new CtoB ratio

cross correlation of the uncorrected vs corrected

