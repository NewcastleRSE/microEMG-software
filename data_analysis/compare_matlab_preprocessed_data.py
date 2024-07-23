#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare preprocessing pipeline to MATLAB preprocessed data.

Files must for this analysis must first be exported from MATLAB script.
"""
import os
import matplotlib.pyplot as plt

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
import pymicroemg.helper_config as cfg
import scipy.io as sio

# increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600


# %% recording and channel to analyse

recording_id = "Stuart_E2"
chan = 10

# matlab file
matlab_file = f"{recording_id}_channel-{chan:03d}.mat"
matlab_path = os.path.join("data_analysis", "matlab_data", matlab_file)

# corresponding data to load using Python module
match recording_id:
    case "Stuart_E2":
        recording_num = 1

python_dir, _ = cfg.get_control_recording_path_and_id(recording_num)

# %% Load data

# matlab file - original, mains removed, and mains removed + filtered (only 1 channel)
matlab_data = sio.loadmat(matlab_path)
sio_keys = ["__header__", "__version__", "__globals__"]
for k in sio_keys:
    matlab_data.pop(k, None)
for k in matlab_data.keys():  # flatten
    matlab_data[k] = matlab_data[k].flatten()

# Python
python_emg_files = EMGFiles(python_dir)
python_data = python_emg_files.load_emg_data()

# %% Compare original data

print(f"Size of Python data: {python_data.emg_ts[chan,].shape}")
print(f"Size of MATLAB data: {matlab_data['original'].shape}")

sum(matlab_data["original"] - python_data.emg_ts[chan - 1,])
sum(matlab_data["original"] - python_data.emg_ts[chan - 1,].astype(int))

# also check int version because MATLAB data is saved as int
# int version may not be the same - differnce in how MATLAB and Python round

# Plot
# Compare MATLAB channel to all Python channels
start_t = 0
stop_t = 5
for python_chan in [chan - 1]:  # range(python_data.n_chan):
    fig, ax = plt.subplots(figsize=[5, 5])

    # Time vector for x axis
    emg_t = python_data.get_emg_t()
    plot_idx = python_data._get_t_idx(start_t, stop_t)

    ax.plot(
        emg_t[plot_idx], matlab_data["original"][plot_idx], "-", lw=0.5, label="original (MATLAB)"
    )
    ax.plot(
        emg_t[plot_idx],
        python_data.emg_ts[python_chan, plot_idx],
        "-",
        lw=0.5,
        label=f"original (Python) {python_chan}",
    )

    lgnd = ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False)

# %% Plot difference between a specific Python channel and the saved MATLAB channel
python_chan = chan - 1  # This channel will match if remove sorting step in Python data import
fig, ax = plt.subplots(figsize=[5, 5])
data_diff = matlab_data["original"] - python_data.emg_ts[python_chan,].astype(int)
ax.plot(emg_t[plot_idx], data_diff[plot_idx])

# %% Compare matlab versions of the data to each other

# All steps
start_t = 1
stop_t = 1.1
emg_t = python_data.get_emg_t()
plot_idx = python_data._get_t_idx(start_t, stop_t)

fig, ax = plt.subplots(figsize=[5, 5])
for k in ["original", "nomains", "filtered"]:
    ax.plot(emg_t[plot_idx], matlab_data[k][plot_idx], "-", lw=0.5, label=f"MATLAB {k}")

lgnd = ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False)

# Just mains removed and filtered
start_t = 1
stop_t = 1.01  # small time period to see phase shift
emg_t = python_data.get_emg_t()
plot_idx = python_data._get_t_idx(start_t, stop_t)

fig, ax = plt.subplots(figsize=[5, 5])
for k in ["nomains", "filtered"]:
    ax.plot(emg_t[plot_idx], matlab_data[k][plot_idx], "-", lw=0.5, label=f"MATLAB {k}")

lgnd = ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False)

# %% Preprocess Python data

preproc_settings = EMGPreprocSettings()

# Just mains noise removal
preproc_settings.add_remove_mains()
python_data_nomains = python_data.preprocess(preproc_settings)

# Add filtering
preproc_settings.add_butterworth_filter(cutoff_freq=[500, 2000], order=4, filter_type="bandpass")
python_data_filtered = python_data.preprocess(preproc_settings)

# %% Compare matlab preprocessing to python preprocessing: mains noise removal

python_chan = chan - 1  # This channel will match if remove sorting step in Python data import

start_t = 299
stop_t = 299.94
emg_t = python_data_nomains.get_emg_t()
plot_idx = python_data_nomains._get_t_idx(start_t, stop_t)

# Plot overlaid traces
fig, ax = plt.subplots(figsize=[5, 5])
ax.plot(emg_t[plot_idx], matlab_data["nomains"][plot_idx], "-", lw=0.5, label="MATLAB, no mains")
ax.plot(
    emg_t[plot_idx],
    python_data_nomains.emg_ts[python_chan, plot_idx],
    "-",
    lw=0.5,
    label="Python, no mains",
)

lgnd = ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False)

# Plot difference
fig, ax = plt.subplots(figsize=[5, 5])
data_diff = matlab_data["nomains"] - python_data_nomains.emg_ts[python_chan]
ax.plot(emg_t, data_diff)
ax.set_title("MATLAB no mains minus Python no mains")


# %% Compare matlab preprocessing to python preprocessing: filtering

python_chan = chan - 1  # This channel will match if remove sorting step in Python data import

start_t = 1
stop_t = 1.1
emg_t = python_data_filtered.get_emg_t()
plot_idx = python_data_filtered._get_t_idx(start_t, stop_t)

# Plot overlaid traces
fig, ax = plt.subplots(figsize=[5, 5])
ax.plot(
    emg_t[plot_idx],
    matlab_data["filtered"][plot_idx],
    "-",
    lw=0.5,
    label="MATLAB, filtered (FIR)",
)
ax.plot(
    emg_t[plot_idx],
    python_data_filtered.emg_ts[python_chan, plot_idx],
    "-",
    lw=0.5,
    label="Python, filtered (IIR)",
)

lgnd = ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False)

# Plot difference
fig, ax = plt.subplots(figsize=[5, 5])
data_diff = matlab_data["filtered"] - python_data_filtered.emg_ts[python_chan]
ax.plot(emg_t, data_diff)
ax.set_title("MATLAB filtered minus Python filtered")
