#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load, visualise, and preprocess example EMG data.

"""

import matplotlib.pyplot as plt

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_data import EMGData
import pymicroemg.helper_config as cfg

# increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600

# %% Choose recording (uncomment one)

recording_num = 0
# recording_num = 1
# %% Load data

# Recording directory and ID
emg_dir, recording_id = cfg.get_recording_path_and_id(recording_num)

# Instantiate EMG files object for emg_dir - will use to load data
emg_files = EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()


# %% Trimming example

# Plot 10 to 20 seconds in the original data
start_t = 10
stop_t = 20
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id}, {start_t} to {stop_t} seconds of original time series")

# Trim original data (time segment 10-110s)
emg_data.trim_emg_ts(start_t=10, stop_t=110)

# Plot 0 to 10 seconds of the trimmed data
# Should match above plot, with shifted time labels
start_t = 0
stop_t = 10
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id}, {start_t} to {stop_t} seconds of trimmed time series")


# %% Preprocessing example

# Create and specify preprocessing settings using EMGPreprocSettings object
preproc_settings = EMGPreprocSettings()
preproc_settings.add_butterworth_filter()  # for defaults
# preproc_settings.add_butterworth_filter(
#    cutoff_freq=[400, 2100], order=4, filter_type='bandpass'
# )
preproc_settings.add_remove_mains()

# Apply preprocessing settings to raw EMG data to generate preprocessed EMG data
emg_data_preproc = emg_data.preprocess(preproc_settings)

# %% Plot part of segment, before and after preprocessing
start_t = 3
stop_t = 4

fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id} raw")

fig, ax = emg_data_preproc.plot_emg_ts(start_t=start_t, stop_t=stop_t)
ax.set_title(f"{recording_id} preprocessed")

# %% PSD example
start_f = 500

# Compute and plot PSD
emg_pxx = emg_data.compute_pxx(10)
emg_pxx.plot_pxx(start_f, 2500, plot_chan=2)

emg_pxx_preproc = emg_data_preproc.compute_pxx(10)
emg_pxx_preproc.plot_pxx(start_f, 2500, plot_chan=2)

# %% Setting data to analyse from preprocessed data

# Sets boolean for timepoints (10-20 s)
emg_data_preproc.set_analyse_t(start_t=10, stop_t=20)

# Sets boolean for channels
bad_chan = [0, 1, 8]
emg_data_preproc.set_bad_chan(bad_chan)

# %% header file

hfile = emg_files.read_header()
# %% Demonstrate that parent class EMGData cannot be instatiated (will throw error)

my_data = EMGData(
    emg_data.emg_ts, emg_data.fs, emg_data.chan, emg_data.segment_of_recording
)
