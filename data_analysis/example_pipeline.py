#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example pipeline for EMG analysis, including motor unit and muscle fibre localisation.

"""
import sys
import os

import matplotlib.pyplot as plt

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
import pymicroemg.helper_config as cfg

try:
    from emg_reconstruct.emg_analysis_reconstruct import EMGAnalysisReconstructSettings
    from emg_reconstruct.emg_analysis_reconstruct import EMGAnalysisReconstruct
except Exception as e:
    print(e)
    print("Adding module to path...")
    # if import fails, add analysis module to path so can use existing import statements
    # TODO: remove once these modules are incorporated into pymicroemg
    path_current = os.getcwd()
    path_reconstruct = os.path.join(path_current, "analysis_software", "analysis")
    sys.path.append(path_reconstruct)

    from emg_reconstruct.emg_analysis_reconstruct import EMGAnalysisReconstructSettings
    from emg_reconstruct.emg_analysis_reconstruct import EMGAnalysisReconstruct

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


# %% Optional: Trim original time series to first minute to speed up analysis

emg_data.trim_emg_ts(start_t=0, stop_t=10)

# %% Optional: Plot specified segment of the EMG recording
start_t = 0
stop_t = 10
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id}, {start_t} to {stop_t}")


# %% Preprocessing

# Create and specify preprocessing settings using EMGPreprocSettings object
# TODO: determine filter settings with Stu
preproc_settings = EMGPreprocSettings()
preproc_settings.add_butterworth_filter(
    cutoff_freq=[10, 2500], order=4, filter_type="bandpass"
)
preproc_settings.add_remove_mains()

# Apply preprocessing settings to raw EMG data to generate preprocessed EMG data
emg_data_preproc = emg_data.preprocess(preproc_settings)

# %% Optional: Plot specified part of segment, before and after preprocessing
start_t = 3
stop_t = 4

fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id} raw")

fig, ax = emg_data_preproc.plot_emg_ts(start_t=start_t, stop_t=stop_t)
ax.set_title(f"{recording_id} preprocessed")

# %% Optional: PSD (one channel)
start_f = 0
stop_f = 10000
plot_chan = 2

# Compute and plot PSD
emg_pxx = emg_data.compute_pxx(window_size=10)
emg_pxx.plot_pxx(start_f, stop_f, plot_chan=plot_chan)

emg_pxx_preproc = emg_data_preproc.compute_pxx(window_size=10)
emg_pxx_preproc.plot_pxx(start_f, stop_f, plot_chan=plot_chan)

# %% Setting data to analyse from preprocessed data

# TODO: either remove option to specifiy timepoints or incorporate into downstream
# analysis

# Mark any bad channels
# TODO: add as a case-switch statement depending on the recording
# TODO: check that incorporated into all downstream analysis
bad_chan = []
emg_data_preproc.set_bad_chan(bad_chan)

# %% Find motor units

# Create settings for this part of the analysis
# TODO: update this step when n_electrodes is removed as attribute
analysis_settings = EMGAnalysisReconstructSettings()
analysis_settings.n_electrodes = emg_data_preproc.n_chan
print(analysis_settings)

# Find motor units
reconstruct = EMGAnalysisReconstruct(emg_data_preproc, analysis_settings)
reconstruct.find_motor_units()

# %% Analyse the motor units
reconstruct_mu = reconstruct.found_motor_units
print(f"Number of motor units: {len(reconstruct_mu)}")
