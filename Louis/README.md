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

### 19th Feb

wrote a peak filtering function for bbp data
- 30 wide median
- scipy lowpass (butter, Wn=0.1) filter
- 40 wide median
- 7 wide mean

also created an alternative method that takes into account the local minima. (this could be a good thing to talk about in writeup!)

rewrote MLD code to attach mixed layer depth info to a profile

### 20/21st Feb

implemented minimum based despiking for the bbp data using interpolated temp and salinity

applied zeroing correction to deep chlorophyll

### 26th Feb

applied nearest night quenching correction to bbp data

### 27th Feb

identified nights/days
despiked beta data

### 28th Feb

used new beta despiking method

chlorophyll deep correction

applied cross correlation

### 1-4th March

Realised cross correlation was poor. Found jumps due to over correcting of the CtoB data. Discussed how to potentially fix (adjusting the entire MLD rather than just the top layer)

### 5th March

created `new_corrections.py` that just uses night correlation and goes over the entire MLD

created more plots in chlorophyll_regression comparing old and new corrections

### 6th March

refactored code base into folders

### 7th and 8th March

compared different preprocessing against the night profiles
plotted a map plot of the chlorophyll

### 12th March

decided to write a paper: 
analysis of photochemical quencing corrections in antarctic chlorophyll data

rewrote preprocessing function handling to allow for pre-processing caching and handling different quenching method functions

### 18th March

added photic depth calculations

fixed mixed layer depths

### 19th March

made repo public



# TO DO


up and down casts

correct that bubble stuff

make some clear transects (of chlorophyll)



# Q's

