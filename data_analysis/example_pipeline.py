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


from pymicroemg.emg_reconstruct import EMGAnalysisReconstructSettings
from pymicroemg.emg_reconstruct import EMGAnalysisReconstruct

# increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600

# %% Choose recording (0 - 5) and set recording-specific properties

recording_num = 1

match recording_num:
    case 1:
        trim_start = 0  # start of segment to analyse
        trim_stop = 30  # end of segment to analyse
        plot_offset_ts = 2000  # spacing for traces in recording time series plot
        plot_offset_mu = 300  # spacing for traces in motor unit recording plot
        bad_chan = []  # indices of bad channels

    case 3:
        trim_start = 60  # start of segment to analyse
        trim_stop = 90  # end of segment to analyse
        plot_offset_ts = 2000  # spacing for traces in recording time series plot
        plot_offset_mu = 300  # spacing for traces in motor unit recording plot
        bad_chan = []  # indices of bad channels

    case 4:
        trim_start = 145  # start of segment to analyse
        trim_stop = 175  # end of segment to analyse
        plot_offset_ts = 2000  # spacing for traces in recording time series plot
        plot_offset_mu = 300  # spacing for traces in motor unit recording plot
        bad_chan = []  # indices of bad channels

    case _:
        trim_start = 0  # start of segment to analyse
        trim_stop = 30  # end of segment to analyse
        plot_offset_ts = 2000  # spacing for traces in recording time series plot
        plot_offset_mu = 300  # spacing for traces in motor unit recording plot
        bad_chan = []  # indices of bad channels
# %% Load data

# Recording directory and ID
emg_dir, recording_id = cfg.get_control_recording_path_and_id(recording_num)

# Instantiate EMG files object for emg_dir - will use to load data
emg_files = EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()


# %% Optional: Trim original time series to speed up analysis

emg_data.trim_emg_ts(start_t=trim_start, stop_t=trim_stop)


# %% Preprocessing
# Note that TK Filter will also filter from 50 to 1000 during the motor unit
# identification step

# Create and specify preprocessing settings using EMGPreprocSettings object
# TODO: determine filter settings with Stu
preproc_settings = EMGPreprocSettings()
preproc_settings.add_butterworth_filter(
    cutoff_freq=[100, 2000], order=6, filter_type="bandpass"
)
preproc_settings.add_remove_mains()

# Apply preprocessing settings to raw EMG data to generate preprocessed EMG data
emg_data_preproc = emg_data.preprocess(preproc_settings)

# %% Optional: Plot specified part of segment, before and after preprocessing
start_t = 0
stop_t = 30

fig, ax = emg_data.plot_emg_ts(
    start_t=start_t, stop_t=stop_t, figsize=(14, 7), offset=plot_offset_ts
)
ax.set_title(f"{recording_id} raw")

fig, ax = emg_data_preproc.plot_emg_ts(
    start_t=start_t, stop_t=stop_t, figsize=(14, 7), offset=plot_offset_ts
)
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
# TODO: check that incorporated into all downstream analysis
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

# Plot MUPs
for i in np.arange(reconstruct.found_motor_units.n_motor_units):
    mu_num = reconstruct.found_motor_units.motor_units[i].motor_unit_number
    print(f"motor unit {mu_num}")

    # avg MUP time series
    fig, ax = reconstruct.plot_average_motor_unit_potential(i, offset=plot_offset_mu)
    ax.set_title(
        f"{recording_id}: Average motor unit potential of motor unit {mu_num + 1}"
    )

    # all traces in one channel (best SNR by default) with average highlighted
    fig, ax, chan_idx = reconstruct.plot_all_potentials_one_channel(motor_unit_idx=i)
    ax.set_title(
        f"{recording_id}: Motor unit potentials of motor unit {mu_num + 1} "
        + f"in channel {chan_idx + 1}"
    )

# %% Fibre localisation
# Settings should be set above in analysis_settings

match recording_num:
    case 1:
        motor_units_for_fibre_localisation = [0, 1, 2]
    case _:
        motor_units_for_fibre_localisation = []

for mu in motor_units_for_fibre_localisation:
    print(f"Reconstructing fibres for motor unit {mu + 1}\n")
    reconstruct.reconstruct_fibres(mu)

# %% Plot fibre localisations (all fibre potentials)

# All motor units
fig, ax = reconstruct.found_motor_units.plot_fibre_potential_locations(
    motor_unit_idx=None,
)
ax.set_title(f"{recording_id}: fibre localisations (all fibre potentials)")

# Individual motor units
for mu_num in motor_units_for_fibre_localisation:
    fig, ax = reconstruct.found_motor_units.plot_fibre_potential_locations(
        motor_unit_idx=mu_num, plot_legend=False
    )
    ax.set_title(
        f"{recording_id}: motor unit {mu_num + 1}"
        + " fibre localisations (all fibre potentials)"
    )

# %% Cluster fibre potentials and plot median locations
for mu_num in motor_units_for_fibre_localisation:
    print(f"Clustering fibres in motor unit {mu_num + 1}")
    reconstruct.found_motor_units.cluster_fibre_potentials(mu_num)
    mu = reconstruct.found_motor_units.motor_units[mu_num]
    print(f"{mu.fibre_clustering_results['n_fibre_clusters']} clusters")
    reconstruct.found_motor_units.plot_fibre_potential_clustering_one_motor_unit(mu_num)
