#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example pipeline for EMG analysis, including motor unit and muscle fibre localisation.

"""
import sys
import os

import matplotlib.pyplot as plt
import numpy as np

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


# %% Optional: Trim original time series to speed up analysis

start_t = 0
stop_t = 30

emg_data.trim_emg_ts(start_t=start_t, stop_t=stop_t)

# %% Optional: Plot specified segment of the EMG recording

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
start_t = 0
stop_t = 30

fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, figsize=(14, 7))
ax.set_title(f"{recording_id} raw")

fig, ax = emg_data_preproc.plot_emg_ts(start_t=start_t, stop_t=stop_t, figsize=(14, 7))
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

# Find motor units

# Create settings for this part of the analysis
# TODO: update this step when n_electrodes is removed as attribute
analysis_settings = EMGAnalysisReconstructSettings()
analysis_settings.n_electrodes = emg_data_preproc.n_chan
print(analysis_settings)

# Find motor units
reconstruct = EMGAnalysisReconstruct(emg_data_preproc, analysis_settings)
reconstruct.find_motor_units()

# %% Visualise/analyse the motor units
# Note MUPs are plotted with the original preprocessed EMG - the second filtering
# step (which produces the time series used for clustering) is not stored.
print(f"Number of motor units: {len(reconstruct.found_motor_units)}")

# Raster plot
fig, ax = reconstruct.plot_motor_units_raster(
    figsize=(14, 7), linelengths=0.75, linewidths=0.75, sort_by="default"
)
ax.set_title(f"Timing of motor unit potentials in {recording_id}")

# Print times of one MU
mu = 0
emg_t = reconstruct.emg_data_preproc.get_emg_t()
print(
    np.round(emg_t[reconstruct.found_motor_units.motor_units[mu].potentials_t_idx], 2)
)


# Plot MUPs
for i in np.arange(reconstruct.found_motor_units.n_motor_units):
    mu_num = reconstruct.found_motor_units.motor_units[i].motor_unit_number

    # avg MUP time series
    fig, ax = reconstruct.plot_average_motor_unit_potential(i, offset=400)
    ax.set_title(f"{recording_id}: Average motor unit potential of motor unit {mu_num}")

    # all traces in one channel (best SNR by default) with average highlighted
    fig, ax, chan_idx = reconstruct.plot_all_potentials_one_channel(motor_unit_idx=i)
    ax.set_title(
        f"{recording_id}: Motor unit potentials of motor unit {mu_num + 1} "
        + f"in channel {chan_idx + 1}"
    )

# Fibre localisation
# Settings should be set above in analysis_settings

motor_units_for_fibre_localisation = [0]

for mu in motor_units_for_fibre_localisation:
    print(f"Reconstructing fibres for motor unit {mu + 1}\n")
    reconstruct.reconstruct_fibres(mu)

# TODO
# Plot fibre localisations?
