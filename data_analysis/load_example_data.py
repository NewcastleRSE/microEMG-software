#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load and plot example EMG data. 

@author: Gabrielle
"""

import os
import pymicroemg.emg_recording as emg_recording

#import matplotlib.pyplot as plt
#import numpy as np

# Directory containing example data
emg_dir = os.path.join('data', 'sample_data_20231124', 'real',
                       'Low quality', 'low amplitude- 20150324', 'raw')

# Instantiate EMG files object for emg_dir - will use to load data
emg_files = emg_recording.EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()

# Plot segment
fig, ax = emg_data.plot_emg_ts(start_t=5, stop_t=12)

#%%

#%%
"""
Notes
    
TODO: do we need info from any files besides the header (info.rhd) and amplifier .dat files?

"""