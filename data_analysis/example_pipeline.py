#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example pipeline for EMG analysis, including motor unit and muscle fibre localisation.

"""

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
import pymicroemg.helper_config as cfg

from pymicroemg.emg_reconstruct_settings import (
    EMGAnalysisReconstructSettings,
    EMGAnalysisMotorUnitSettings,
    EMGAnalysisMotorUnitClusterSettings,
    EMGAnalysisMotorUnitJitterSettings,
)

# increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600

# %% Choose recording (0 - 5) and set recording-specific properties

recording_num = 1

match recording_num:
    case 1:
        trim_start = 0  # start of segment to analyse
        trim_stop = 60  # end of segment to analyse
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
preproc_settings.add_butterworth_filter(cutoff_freq=[100, 2000], order=6, filter_type="bandpass")
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
emg_data_preproc.set_bad_chan(bad_chan)

# Find motor units

# Create settings for this part of the analysis
mu_settings = EMGAnalysisMotorUnitSettings()
recon_settings = EMGAnalysisReconstructSettings()
# Create cluster settings and jitter analysis settings needed later
mu_cluster_settings = EMGAnalysisMotorUnitClusterSettings()
mu_jitter_settings = EMGAnalysisMotorUnitJitterSettings()

# Find motor units
reconstruct = emg_data_preproc.set_up_reconstruct_analysis(
    mu_settings, recon_settings, mu_cluster_settings, mu_jitter_settings
)
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
    ax.set_title(f"{recording_id}: Average motor unit potential of motor unit {mu_num + 1}")

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
        motor_units_for_fibre_localisation = [1]
    case 3:
        motor_units_for_fibre_localisation = [0, 1, 2]

for mu in motor_units_for_fibre_localisation:
    print(f"Reconstructing fibres for motor unit {mu + 1}\n")
    reconstruct.reconstruct_fibres(mu)

# %% Plot fibre localisations (all fibre potentials)

# All motor units

# Potentials
fig, ax = reconstruct.found_motor_units.plot_fibre_locations(
    "potentials",
    motor_unit_idx=None,
)
ax.set_title(f"{recording_id}: fibre localisations (all fibre potentials)")


# Individual motor units
for mu_num in motor_units_for_fibre_localisation:
    fig, ax = reconstruct.found_motor_units.plot_fibre_locations(
        "potentials", motor_unit_idx=mu_num, plot_legend=False
    )
    ax.set_title(
        f"{recording_id}: motor unit {mu_num + 1}" + " fibre localisations (all fibre potentials)"
    )

# Cluster fibre potentials and plot estimated locations
for mu_num in motor_units_for_fibre_localisation:
    print(f"Clustering fibres in motor unit {mu_num + 1}")
    reconstruct.mu_cluster_fibre_potentials(mu_num)

    mu = reconstruct.found_motor_units.motor_units[mu_num]
    print(f"{mu.fibre_clustering_results['n_fibre_clusters']} clusters")
    mu.plot_fibre_potential_clustering()

    clustering_results = mu.fibre_clustering_results

# Estimated fibre locations of all motor units (median only)
fig, ax = reconstruct.found_motor_units.plot_fibre_locations("fibres", motor_unit_idx=None)
ax.set_title("Fibre locations of all motor units")

# %% TODO: need to start new plot for jitter

# Perform jitter analyses.
for mu_num in motor_units_for_fibre_localisation:
    # Do jitter analysis
    reconstruct.mu_jitter_analysis(mu_num)

    # Plot heat plot of mean consectutive differences (MCDs).
    mu = reconstruct.found_motor_units.motor_units[mu_num]
    mu.plot_jitter_heat_plot()

    jitter_results = mu.fibre_jitter_results


# %% develop jitter plot

# 008080,#70a494,#b4c8a8,#f6edbd,#edbb8a,#de8a5a,#ca562c
mu_idx = 1
mu = reconstruct.found_motor_units.motor_units[mu_idx]

# inputs
# no ax input since includes subplots
fibre1 = 1
fibre2 = 0
fibre_clrs = None  # list[Any] | None = None

emg_line_lw = 1
emg_line_alpha = 0.25
time_marker_size = 2

align_times_to_fibre1 = True

figsize = (10, 10)
axis_label_size = 12
title_size = 14
dpi = 300
downsample_factor = 1


# if fibre1 and 2 have the same value, value error - need two different fibres for jitter
if fibre_clrs is None:
    fibre_clrs = ["#008080", "#ca562c"]

# Determine MUPs and fibres used for jitter computation

# Jitter results
jitter_results = mu.fibre_jitter_results

# Get indices of fibre 1 and fibre 2 (in fibre_potential_times/fibre_potential_peak_chan)
# for each MUP that was analysed
# First need to determine which fields to use for each fibre
# Lower fibre number is stored in fibre1 results, while higher value is fibre2

fibre_pair_idx = mu.get_jitter_fibre_pair_idx(fibre1, fibre2)
print(fibre_pair_idx)
if fibre_pair_idx is None:
    raise ValueError("Requested fibre pair is not an option.")

if fibre1 < fibre2:
    # Indices in fibre_potential_times
    fibre1_pot_used_idx_field = "fibre1_pot_used_idx"
    fibre2_pot_used_idx_field = "fibre2_pot_used_idx"
else:
    # Indices in fibre_potential_times
    fibre2_pot_used_idx_field = "fibre1_pot_used_idx"
    fibre1_pot_used_idx_field = "fibre2_pot_used_idx"


# Get mean consecutive difference of that fibre pair
# If doesn't exist, return early
mcd = jitter_results["mean_consecutive_diffs"][fibre_pair_idx]
if np.isnan(mcd):
    raise ValueError("No results for that fibre pair")

# Initialise array for storing which MUPs were analysed
analysed_mup = np.full(mu.n_potentials, False)

# Need to append and prepend NaN to consecutive differences array to determine which
# MUPs are used (since each consecutive difference corresponds to two MUPs)
nan1 = np.isnan(np.append(jitter_results["consecutive_diffs"][fibre_pair_idx, :], np.nan))
nan2 = np.isnan(
    np.append(np.array(np.nan), jitter_results["consecutive_diffs"][fibre_pair_idx, :])
)

# if not nan in at least one, that MUP was analysed analysed
analysed_mup[np.any([~nan1, ~nan2], axis=0)] = True

# Indices of fibres 1 and 2 in each MUP
analysed_fibres_idx = np.vstack(
    (
        jitter_results[fibre1_pot_used_idx_field][fibre_pair_idx, :],
        jitter_results[fibre2_pot_used_idx_field][fibre_pair_idx, :],
    )
)
analysed_fibres_idx[:, ~analysed_mup] = np.nan  # nan if fibre not analysed

# TODO: check that mup_onsets is the same for each pair of indices in analysed_fibre_idx
# i.e., to confirm the fibres belong to the same MUP

# Get fibre information

# Get
# 1) mode of the peak channels of fibre 1 and fibre 2 and
# 2) times of the fibre potentials in the each MUP (nan if not analysed)
n_fibres = 2
fibres_peak_chan = np.full(n_fibres, 0)
analysed_fibre_t = np.full((mu.n_potentials, n_fibres), np.nan)  # will be nan if not analysed
for i in range(n_fibres):  # for each fibre
    # int indices of the analysed fibres, without nan (so can use for indexing)
    idx = analysed_fibres_idx[i, :]
    idx_no_nan = idx[~np.isnan(idx)]
    idx_no_nan = idx_no_nan.astype(int)

    # Peak channel for each fibre and mode of peak channels
    chan = mu.fibre_potential_peak_chan[idx_no_nan]
    print(chan)
    mode_i = scipy.stats.mode(chan)
    print(mode_i)
    fibres_peak_chan[i] = int(mode_i[0])

    # Fibre times for each mup if mup was analysed (i.e., idx is not nan)
    fibre_t = np.full(mu.n_potentials, np.nan)
    analysed_fibre_t[~np.isnan(idx), i] = mu.fibre_potential_times[idx_no_nan]

# Convert fibre times to ms
analysed_fibre_t = (analysed_fibre_t / reconstruct.emg_data_preproc.fs) * 1000


# EMG traces - times

# Create time vectors (ms) for x-axis of MUP EMG traces (analysed MUP only)
# Will create a separate column for each trace so can align based on fibre potential
# times if requested
mup_t = (np.arange(1, mu.all_spikes.shape[2] + 1) / reconstruct.emg_data_preproc.fs) * 1000
mup_t = np.transpose(np.tile(mup_t, [mu.n_potentials, 1]))  # repeat and transpose (column = mup)


# If requested, re-align times so fibre1 times = 0
if align_times_to_fibre1:
    # Subtract fibre1 times from MUP times
    n_t = mup_t.shape[0]
    mup_t = mup_t - np.tile(analysed_fibre_t[:, 0], [n_t, 1])

    # Subtract fibre1 times from analysed fibre times
    # (must be done second since need original fibres times for changing MUP times)
    analysed_fibre_t = analysed_fibre_t - np.transpose(
        np.tile(analysed_fibre_t[:, 0], [n_fibres, 1])
    )


# EMG traces

# Set up plot
fig, axs = plt.subplots(3, 1, figsize=figsize, height_ratios=[1, 1, 4], sharex=True)
fig.dpi = dpi

# Plot MUPs of each fibre in each fibre's "peak" channel

# Labels for fibres (add 1 to count from 1)
fibre_labels = [fibre1 + 1, fibre2 + 1]

# Plot
for i in range(n_fibres):
    axs[i].plot(
        mup_t[0::downsample_factor, analysed_mup],
        np.transpose(
            np.squeeze(mu.all_spikes[analysed_mup, fibres_peak_chan[i], 0::downsample_factor])
        ),
        lw=emg_line_lw,
        color=fibre_clrs[i],
        alpha=emg_line_alpha,
    )
    # Labels (add one to indices so count is from 1 in labels)
    axs[i].set_title(
        f"fibre {fibre_labels[i]}, channel {fibres_peak_chan[i] + 1}", fontsize=title_size
    )
    axs[i].set_ylabel("\u03bcV", fontsize=axis_label_size)
    # No x-axis label since shared across all plots

# Link y-axes of two EMG plots
axs[1].sharey(axs[0])

# Fibre timing

# Plot times of the two fibre potentials in each MUPs
mup_number = np.arange(mu.n_potentials) + 1  # sets y axis location of each tick
ax_times = 2  # axis to use for plot
for i in range(n_fibres):
    axs[ax_times].scatter(
        analysed_fibre_t[:, i], mup_number, s=time_marker_size, marker="|", color=fibre_clrs[i]
    )
axs[ax_times].set_ylim([1, max(mup_number)])
axs[ax_times].invert_yaxis()  # first MUP at the top of the plot
# Labels
axs[ax_times].set_title("fibre potential times", fontsize=title_size)
axs[ax_times].set_ylabel("motor unit potential", fontsize=title_size)
if align_times_to_fibre1:
    axs[ax_times].set_xlabel(
        f"time (ms) relative to fibre {fibre_labels[0]} peak", fontsize=axis_label_size
    )
else:
    axs[ax_times].set_xlabel("time (ms)", fontsize=axis_label_size)
axs[ax_times].set_xlim(
    [np.nanmin(mup_t), np.nanmax(mup_t)]
)  # keeps x-axis limits tight for all plots

# TODO: need to remove outliers (maybe get threshold for removing outliers so can
# identify which differences are outliers)
