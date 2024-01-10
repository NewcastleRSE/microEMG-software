#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load, visualise, and preprocess example EMG data. 

"""

import os
from pymicroemg.emg_files import EMGFiles

import matplotlib.pyplot as plt
import numpy as np

import scipy.signal

# increase figure resolution (needed for Spyder IDE)
plt.rcParams['figure.dpi'] = 600

#%% Choose recording (uncomment one)

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
emg_files = EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()


#%% Trimming example

# Plot 10 to 20 seconds in the original data
start_t = 10
stop_t = 20
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset = 2000)
ax.set_title(f'{recording_ID}, {start_t} to {stop_t} seconds of original time series');

# Trim original data (time segment 10-110s)
emg_data.trim_emg_ts(start_t=10, stop_t=110)

# Plot 0 to 10 seconds of the trimmed data
# Should match above plot, with shifted time labels
start_t = 0
stop_t = 10
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset = 2000)
ax.set_title(f'{recording_ID}, {start_t} to {stop_t} seconds of trimmed time series');

#%% Filtering example

# Plot part of segment, before filtering
start_t = 30
stop_t = 40
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset = 2000)
ax.set_title(f'{recording_ID} raw');

# Bandpass filter
emg_data.butterworth_filter()

# Plot same segment, after filtering
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t)
ax.set_title(f'{recording_ID} filtered')

#%% PSD example

# Compute and plot PSD
emg_pxx = emg_data.compute_pxx(100)
emg_pxx.plot_pxx(400, 2500, plot_chan=34)