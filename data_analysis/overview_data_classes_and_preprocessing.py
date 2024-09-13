"""
Overview of data classes and preprocessing steps for microEMG data.
"""

import matplotlib.pyplot as plt
import numpy as np

from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg import helper_config as cfg

from pymicroemg.emg_reconstruct_settings import (
    EMGAnalysisReconstructSettings,
    EMGAnalysisMotorUnitSettings,
    EMGAnalysisMotorUnitClusterSettings,
    EMGAnalysisMotorUnitJitterSettings,
)

# increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600

# %% Load data

# Recording's directory and ID
recording_num = 0
emg_dir, recording_id = cfg.get_recording_path_and_id(recording_num)

# %% EMGFiles

# The EMGFiles class is used to represent a set of recording files (.dat files and the
# Intan header file). It has a method for loading the data, which creates an EMGDataRaw
# object containing the EMG time series and channel information.

# Instantiate EMG files object
emg_files = EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()

# %% EMGData, EMGDataRaw, and EMGDataPreproc
# There are two classes that can be used to represent EMG time series data: EMGDataRaw
# for the "raw" original data, and EMGDataPreproc for the preprocessed (e.g., filtered)
# data. This distinction is used to separate methods with different functions that
# should be applied at different points in the analysis:
#   - EMGDataRaw has methods for preprocessing.
#   - EMGDataPreproc has methods for selecting the data to analyse and (will have)
#       methods for downstream analysis (e.g., identifying motor units) (these methods
#       should )
# Thus, this approach ensures that certain methods can only be applied at a certain
# stage of the data analysis.
# Their parent class, EMGData, sets up the attributes and provides shared methods (e.g.,
# for visualisation). EMGData cannot be directly instantiated.


# %% Channels
# The "chan" attribute in EMGDataRaw and EMGDataPreproc stores channel information as
# an instance of the EMGChannels class:
print(type(emg_data.chan))

# This class stores information about channel names and (x, y) coordinates (the latter
# were previously stores as a "needle model" in the original software).
print(emg_data.chan.chan_names)
print(emg_data.chan.chan_xy)

# %% Trimming and plotting example
# You can "trim" the time period used for the analysis using the trim_emg_ts method.
# This method discards the data that is not used for the analysis.

# Plot 10 to 20 seconds in the original data
start_t = 10
stop_t = 20

# "offset" controls the amount of space between the channels' signals (and thus their
# apparent amplitude in the plot)
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id}, {start_t} to {stop_t} seconds of original time series")

# Trim original data (keep time segment 10-110s)
emg_data.trim_emg_ts(start_t=10, stop_t=110)

# Plot 0 to 10 seconds of the trimmed data
# Should match above plot, with shifted time labels
start_t = 0
stop_t = 10
fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id}, {start_t} to {stop_t} seconds of trimmed time series")

# %% EMGPreprocSettings
# To make it easy to store and apply user input from the GUI, we have a class for
# representing the preprocessing settings, EMGPreprocSettings. When the class is
# instantiated, no preprocessing steps are specified. Each preprocessing step (and its
# settings) are added using the class's methods. The settings below should be fine as a
# starting point.

# Create and specify preprocessing settings using EMGPreprocSettings object
preproc_settings = EMGPreprocSettings()

# Add filter (default settings)
preproc_settings.add_butterworth_filter()

# Add mains noise removal.
# There are some optional paramaters that can be changed, but that option will not be
# provided in the GUI - it's fine to use the default.
preproc_settings.add_remove_mains()

# Apply the preprocessing settings to raw EMG data to generate preprocessed EMG data
# (class EMGDataPreproc)
emg_data_preproc = emg_data.preprocess(preproc_settings)

# %% Plot part of segment, before and after preprocessing
start_t = 3
stop_t = 4

fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
ax.set_title(f"{recording_id} raw")

fig, ax = emg_data_preproc.plot_emg_ts(start_t=start_t, stop_t=stop_t)
ax.set_title(f"{recording_id} preprocessed")

# %% Selecting data to analysis
#
# After preprocessing, the user will get the option to limit the data analysed to
# specific channels in the recording. This step create a boolean array of which channels
# to use for the analysis.
#
# No data is discard in this step - the full EMG time series array stays the same. This
# approach allows the data selection to easily be changed if the user decides their
# initial choice isn't suitable for the analysis. As such, any downstream analysis
# methods must use these attributes to limit the data that is analysed.

# Set boolean for channels
# It's more standard in EMG/EEG analysis to mark "bad" channels that should be removed
# from the analysis, rather than "good" channels to use.
# Bad channels are indicated by index (counting from zero), not name (counting from 1)
# These channels are arbitrarily selected as an example - they are fine to use in the
# analysis!
bad_chan = list(np.arange(2, 13)) + [26] + [30] + list(np.arange(34, 53))
emg_data_preproc.set_bad_chan(bad_chan)
print("Channels to analyse: ")
for i in range(emg_data.n_chan):
    if emg_data_preproc.chan.analyse_chan[i]:
        print(f"{emg_data_preproc.chan.chan_names[i]} (idx {i})")

# %% PSDs

# There is also a class for representing power spectral densities (EMGPxx) - we can
# use the corresponding visualisation to confirm that the preprocessing steps were
# appropriate. This class should not be needed for the downstream analysis.

pxx_win_size = 10  # window size for PSD calculations

# PSD requencies to compute and plot
start_freq = 0
stop_freq = 5000
plot_chan = 2  # channel to plot (index, counting from 0)

# Compute and plot PSD before and after preprocessing
emg_pxx = emg_data.compute_pxx(window_size=pxx_win_size)
emg_pxx.plot_pxx(start_freq=start_freq, stop_freq=stop_freq, plot_chan=plot_chan)
emg_pxx_preproc = emg_data_preproc.compute_pxx(window_size=pxx_win_size)
emg_pxx_preproc.plot_pxx(start_freq=start_freq, stop_freq=stop_freq, plot_chan=plot_chan)

# %% Motor units and fibres analyses

# All downstream analyses are handled by the EMGAnalysisReconstruct class, which can be
# created from the preprocessed data. See the example_pipeline.py script for examples of
# these analyses.

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
