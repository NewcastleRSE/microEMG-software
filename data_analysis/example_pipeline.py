#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example pipeline for the microEMG analysis, including motor unit identification, muscle
fibre localisation, and jitter analysis.

"""
import json
import matplotlib.pyplot as plt
import numpy as np

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
import pymicroemg.helper_config as cfg

from pymicroemg.emg_reconstruct_settings import (
    EMGAnalysisReconstructSettings,
    EMGAnalysisMotorUnitSettings,
    EMGAnalysisMotorUnitClusterSettings,
    EMGAnalysisMotorUnitJitterSettings,
)


# Increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600

# %% Choose recording (currently only option is 0) and set recording-specific properties

recording_num = 0


match recording_num:
    case 0:  # 0 corresponds to the Stuart_E2 recording
        trim_start = 0  # start of segment to analyse
        trim_stop = 60  # end of segment to analyse
        plot_offset_ts = 2000  # spacing for traces in recording time series plot
        plot_offset_mu = 300  # spacing for traces in motor unit recording plot
        bad_chan = []  # indices of bad channels
# %% Load data

# Recording directory and ID
emg_dir, recording_id = cfg.get_recording_path_and_id(recording_num)

# Instantiate EMG files object for emg_dir - will use to load data
emg_files = EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()


# %% Optional: Trim original time series to only use that section of the recording for
# the analysis. Will speed up the computations.

emg_data.trim_emg_ts(start_t=trim_start, stop_t=trim_stop)

# %% Preprocessing
# Note that TK Filter will also filter from 50 to 1000 Hz during the motor unit
# identification step (but this filtering is discarded after identifying motor units).

# Create and specify preprocessing settings using EMGPreprocSettings object
preproc_settings = EMGPreprocSettings()
preproc_settings.add_butterworth_filter(cutoff_freq=[100, 2000], order=6, filter_type="bandpass")
preproc_settings.add_remove_mains()  # also remove mains noise

# Apply preprocessing settings to raw EMG data to generate preprocessed EMG data
emg_data_preproc = emg_data.preprocess(preproc_settings)

# %% Optional: Plot specified part of segment, before and after preprocessing
start_t = trim_start
stop_t = trim_stop

fig, ax = emg_data.plot_emg_ts(
    start_t=start_t, stop_t=stop_t, figsize=(14, 7), offset=plot_offset_ts
)
ax.set_title(f"{recording_id} raw")

fig, ax = emg_data_preproc.plot_emg_ts(
    start_t=start_t, stop_t=stop_t, figsize=(14, 7), offset=plot_offset_ts
)
ax.set_title(f"{recording_id} preprocessed")

# %% Optional: Compute and plot the PSD of one channel
start_f = 0  # Frequency range to compute for PSD
stop_f = 5000
plot_chan = 0  # Channel in terms of index

# Compute and plot PSD
emg_pxx = emg_data.compute_pxx(window_size=10)
emg_pxx.plot_pxx(start_f, stop_f, plot_chan=plot_chan)

emg_pxx_preproc = emg_data_preproc.compute_pxx(window_size=10)
emg_pxx_preproc.plot_pxx(start_f, stop_f, plot_chan=plot_chan)

# %% Mark any bad channels - will be excluded from the analysis
emg_data_preproc.set_bad_chan(bad_chan)

# %% Set up downstream analysis

# Create settings for this part of the analysis
mu_settings = EMGAnalysisMotorUnitSettings()
recon_settings = EMGAnalysisReconstructSettings()

# Create cluster settings and jitter analysis settings (needed later)
mu_cluster_settings = EMGAnalysisMotorUnitClusterSettings()
mu_jitter_settings = EMGAnalysisMotorUnitJitterSettings()

# Create object for motor unit identification and fibre localisation ("reconstruction").
# This object will be used for all downstream analysis.
reconstruct = emg_data_preproc.set_up_reconstruct_analysis(
    mu_settings, recon_settings, mu_cluster_settings, mu_jitter_settings
)

# %% Find motor units
reconstruct.find_motor_units()

# Visualise/analyse the motor units
# Note MUPs are plotted with the original preprocessed EMG - the second filtering
# step (which produces the time series used for clustering) is not stored.
print(f"Number of motor units: {len(reconstruct.found_motor_units)}")

# Raster plot of times of motor unit potentials
fig, ax = reconstruct.plot_motor_units_raster(
    figsize=(14, 7), linelengths=0.75, linewidths=0.75, sort_by="default"
)
ax.set_title(f"Timing of motor unit potentials in {recording_id}")

# Plot EMG of each MUP
for i in np.arange(reconstruct.found_motor_units.n_motor_units):
    mu_num = reconstruct.found_motor_units.motor_units[i].motor_unit_number
    print(f"motor unit {mu_num}")

    # avgerage MUP time series (across time)
    fig, ax = reconstruct.plot_average_motor_unit_potential(i, offset=plot_offset_mu)
    ax.set_title(f"{recording_id}: Average motor unit potential of motor unit {mu_num + 1}")

    # Plot all traces in one channel (best signal-to-noise ratio by default) with
    # average trace highlighted
    fig, ax, chan_idx = reconstruct.plot_all_potentials_one_channel(motor_unit_idx=i)
    ax.set_title(
        f"{recording_id}: Motor unit potentials of motor unit {mu_num + 1} "
        + f"in channel {chan_idx + 1}"
    )

# %% Fibre localisation

# Choose with motor units to analyse (number of motor units will depend on recording and
# earlier settings). Numeric labels start at 0 in code, but 1 will be added for plot
# labels.
match recording_num:
    case 0:
        motor_units_for_fibre_localisation = [0, 1]

for mu_num in motor_units_for_fibre_localisation:
    print(f"Reconstructing fibres for motor unit {mu_num + 1}\n")
    reconstruct.reconstruct_fibres(mu_num)

# %% Plot fibre localisations (i.e., estimates from all fibre potentials)

# Potentials of all motor units
fig, ax = reconstruct.found_motor_units.plot_fibre_locations(
    "potentials",
    motor_unit_idx=None,
)
ax.set_title(f"{recording_id}: fibre localisations (all fibre potentials)")


# Potentials of individual motor units
for mu_num in motor_units_for_fibre_localisation:
    fig, ax = reconstruct.found_motor_units.plot_fibre_locations(
        "potentials", motor_unit_idx=mu_num, plot_legend=False
    )
    ax.set_title(
        f"{recording_id}: motor unit {mu_num + 1}" + " fibre localisations (all fibre potentials)"
    )

# %% Cluster fibre potentials to determine fibre locations and plot fibre locations

for mu_num in motor_units_for_fibre_localisation:
    print(f"Clustering fibres in motor unit {mu_num + 1}")
    reconstruct.mu_cluster_fibre_potentials(mu_num)

    mu = reconstruct.found_motor_units.motor_units[mu_num]
    print(
        f"Motor unit {mu_num + 1} has {mu.fibre_clustering_results['n_fibre_clusters']}"
        + " fibres"
    )
    mu.plot_fibre_potential_clustering()

    # Clustering results are stored in mu.fibre_clustering_results, where mu is a motor unit

# Estimated fibre locations of all motor units (averaged across all potentials)
fig, ax = reconstruct.found_motor_units.plot_fibre_locations("fibres", motor_unit_idx=None)
ax.set_title("Fibre locations of all motor units")

# %% Perform jitter analyses

for mu_num in motor_units_for_fibre_localisation:
    # Compute jitter
    reconstruct.mu_jitter_analysis(mu_num)

    # Plot heat plot of mean consectutive differences (MCDs).
    mu = reconstruct.found_motor_units.motor_units[mu_num]
    fig, ax = mu.plot_jitter_heat_plot()
    fig, ax = mu.plot_jitter_totals_heat_plot()

    # Jitter results are stored in mu.fibre_jitter_results, where mu is a motor unit

# %% Jitter plot of one fibre pair (EMG traces and times)

# Motor unit to plot
mu_idx = motor_units_for_fibre_localisation[0]

# Fibres to plot (count from 0; 1 will be added to labels for plot)
fibre1 = 0
fibre2 = 1

# Plot
mu = reconstruct.found_motor_units.motor_units[mu_idx]
mu.plot_jitter_fibre_pair_EMG_and_times(fibre1=fibre1, fibre2=fibre2)

# %% Export results
# Test saving all results and settings, and then test loading
filename_json = "microEMG_results_and_settings.json"

# Save results
# By default, does not save EMG traces of MUPs or any EMG data (creates large files)
reconstruct.save_all_results_and_settings(filename_json)

# Can load back into an EMGAnalysisReconstruct object (will overwrite existing results)
reconstruct.load_all_results_and_settings(filename_json)

# Alternatively, load JSON as dictionary
with open(filename_json, "r") as file:
    json_results = json.load(file)

# Top-level JSON fields
print(json_results.keys())

# Example parts of the JSON
print(json.dumps(json_results["emg_info"], indent=4))
print(json.dumps(json_results["recon_settings"], indent=4))
