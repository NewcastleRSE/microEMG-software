#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load and plot example EMG data. 

@author: Gabrielle
"""

import os
import pymicroemg.emg_recording as emg_recording

import matplotlib.pyplot as plt
import numpy as np

# increase figure resolution (needed for Spyder IDE)
plt.rcParams['figure.dpi'] = 600

#%% choose recording (uncomment one)
#recording_ID = 'low amplitude- 20150324'
recording_ID = 'Stuart_E2'

#%% Load data

# Directory containing example data
match recording_ID:
    case 'low amplitude- 20150324':
        emg_dir = os.path.join('data', 'sample_data_20231124', 'real',
                               'Low quality', recording_ID, 'raw')
    case 'Stuart_E2':
        emg_dir = os.path.join('data', 'sample_data_20231124', 'real',
                               recording_ID, 'raw')

# Instantiate EMG files object for emg_dir - will use to load data
emg_files = emg_recording.EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()

# Plot part of segment, before preprocessing
start_t = 1
stop_t = 1.1
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t)
ax.set_title(f'{recording_ID} raw')

#%% Bandpass filter
emg_data = emg_files.load_emg_data()
emg_data.butterworth_filter()

#%% Plot part of segment, after filtering
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t)
ax.set_title(f'{recording_ID} filtered')

#%%
#plt.rcParams['figure.dpi'] = 300
#fig, ax = emg_data.plot_emg_ts()

#%%
"""
Notes
    
TODO: do we need info from any files besides the header (info.rhd) and amplifier .dat files?

"""