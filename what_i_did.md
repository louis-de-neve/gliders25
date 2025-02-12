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

Created [transect indices](Louis/transect_information.py) denoting the start and end indexes of the transects A through J. `all_transect_indexes`

Manually checked each transect to highlight [problematic up/down casts.](Louis/transect_information.py) `transect_problems`

removed problematic down/upcasts and fixed where signal processing had offset casts

started working on a method to convert downcast numbers to distances/times
