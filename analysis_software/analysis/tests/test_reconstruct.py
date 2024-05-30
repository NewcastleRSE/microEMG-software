# Avoid black formating for this test file
# fmt: off
#
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load, visualise, and preprocess example EMG data.

Initially taken from GS code to preprocess data

"""

import os
import re
import matplotlib.pyplot as plt

from pymicroemg.emg_data_preproc import EMGDataPreproc
from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_data import EMGData

from emg_reconstruct.emg_analysis_reconstruct import EMGAnalysisReconstructSettings
from emg_reconstruct.emg_analysis_reconstruct import EMGAnalysisReconstruct
from emg_reconstruct.emg_analysis_reconstruct import EMGMotorUnit

name = "nrajh" #"nrajh" #
        
# increase figure resolution (needed for Spyder IDE)
plt.rcParams["figure.dpi"] = 600

# %% Choose recording (uncomment one)

# recording_ID = 'low amplitude- 20150324'
recording_ID = "Stuart_E2"

# %% Load data

# Directory containing example data
match recording_ID:
    case "low amplitude- 20150324":
        emg_dir = os.path.join(
            "data", "sample_data_20231124", "real", "Low quality", recording_ID, "raw"
        )
    case "Stuart_E2":
        emg_dir = "C:\\Users\\" + name + "\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\multi-emg\\data\\sample_data_20231116\\original_data\\Stuart_E2\\raw"
        #emg_dir = "C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\multi-emg\\data\\sample_data_20231116\\original_data\\Stuart_E2\\raw"
        #emg_dir = os.path.join(
        #    "data", "sample_data_20231124", "real", recording_ID, "raw"            
        #)

# Instantiate EMG files object for emg_dir - will use to load data
emg_files = EMGFiles(emg_dir)

# Load data
emg_data = emg_files.load_emg_data()


# %% Trimming example

# Plot 10 to 20 seconds in the original data
#start_t = 10
#stop_t = 20
#fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
#ax.set_title(f"{recording_ID}, {start_t} to {stop_t} seconds of original time series")

# Trim original data (time segment 10-110s)
#emg_data.trim_emg_ts(start_t=10, stop_t=110)

# Plot 0 to 10 seconds of the trimmed data
# Should match above plot, with shifted time labels
#start_t = 0
#stop_t = 10
#fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
#ax.set_title(f"{recording_ID}, {start_t} to {stop_t} seconds of trimmed time series")


# %% Preprocessing example

# Create and specify preprocessing settings using EMGPreprocSettings object
preproc_settings = EMGPreprocSettings()

preproc_settings.add_butterworth_filter()  # for defaults

preproc_settings.add_butterworth_filter(
    cutoff_freq=[400, 2100], order=4, filter_type='bandpass'
 )

preproc_settings.add_remove_mains()


# Apply preprocessing settings to raw EMG data to generate preprocessed EMG data
emg_data_preproc = emg_data.preprocess(preproc_settings)

# %% Plot part of segment, before and after preprocessing
#start_t = 3
#stop_t = 4

#fig, ax = emg_data.plot_emg_ts(start_t=start_t, stop_t=stop_t, offset=2000)
#ax.set_title(f"{recording_ID} raw")

#fig, ax = emg_data_preproc.plot_emg_ts(start_t=start_t, stop_t=stop_t)
#ax.set_title(f"{recording_ID} preprocessed")

# %% PSD example
#start_f = 500

# Compute and plot PSD
#emg_pxx = emg_data.compute_pxx(10)
#emg_pxx.plot_pxx(start_f, 2500, plot_chan=2)

#emg_pxx_preproc = emg_data_preproc.compute_pxx(10)
#emg_pxx_preproc.plot_pxx(start_f, 2500, plot_chan=2)

# %% Setting data to analyse from preprocessed data

# Sets boolean for timepoints (10-20 s)
#emg_data_preproc.set_analyse_t(start_t=10, stop_t=20)

# Sets boolean for channels
# bad_chan = [0, 1, 8]
# emg_data_preproc.set_bad_chan(bad_chan)

# %% header file

#hfile = emg_files.read_header()
# %% Demonstrate that parent class EMGData cannot be instatiated (will throw error)

#my_data = EMGData(
#    emg_data.emg_ts, emg_data.fs, emg_data.chan, emg_data.segment_of_recording
#)

#my_data = EMGDataPreproc(
#    emg_data.emg_ts, emg_data.fs, emg_data.chan, emg_data.segment_of_recording, preproc_settings
#)


print(preproc_settings)

analysis_settings = EMGAnalysisReconstructSettings()

# Set the number of electrodes, same as the number of channels?
analysis_settings.n_electrodes = emg_data_preproc.emg_ts.shape[0]

print(analysis_settings)

print("Processed data shape: ")
print(emg_data_preproc.emg_ts.shape)

import time

t0 = time.time()

reconstruct = EMGAnalysisReconstruct(emg_data_preproc, analysis_settings)

t0 = time.time()
print("Loading test data...\n")
#Set same data as MATLAB for testing...
filename = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\processed_multi_emg_matlab.csv'
reconstruct.load_data(filename)
t1 = time.time()
total = t1-t0
print("Time = ")
print(total)

#print("Finding motor units...\n")
#reconstruct.find_motor_units()

reconstruct.add_motor_units(64)
t2 = time.time()
total = t2-t1
print("Time = ")
print(total)

#input("Stop...")

filename_locs = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\loc_test_data.csv'
filename_indices = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\index_test_data.csv'
reconstruct.load_motor_unit_data_from_matlab(filename_indices, filename_locs)

print("Reconstructing fibres for MU 0...\n")
reconstruct.reconstruct_fibres(0)
t3 = time.time()
total = t3-t2
print("Time = ")
print(total)

motor_units = reconstruct.found_motor_units

# To separate different test output
extra_label = "_filters3_" #"_highest3_" #"_filters2_" # "_highest2_" #"_filters_"

tX = time.time()

total = tX-t0

print("Total Time =")
print(total)

#output results
name = "nrajh"
output_dir = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\'

import pandas as pd

for motor_unit in motor_units.motor_units:
    pd.DataFrame(motor_unit.fibre_centres).to_csv(output_dir + 'py_fibre_centres' + extra_label + str(motor_unit.motor_unit_number) + '.csv', header= False, index=False, na_rep='nan')
    pd.DataFrame(motor_unit.mean_spikes).to_csv(output_dir + 'py_mean_spikes' + extra_label + str(motor_unit.motor_unit_number) + '.csv', header= False, index=False, na_rep='nan')
    pd.DataFrame(motor_unit.onsets).to_csv(output_dir + 'py_onsets' + extra_label + str(motor_unit.motor_unit_number) + '.csv', header= False, index=False, na_rep='nan')    
    pd.DataFrame(motor_unit.gn_potential).to_csv(output_dir + 'py_gn_potential' + extra_label + str(motor_unit.motor_unit_number) + '.csv', header= False, index=False, na_rep='nan')
    # Not 2D, not sure how MATLAB handled this!
    #pd.DataFrame(motor_unit.all_spikes).to_csv(output_dir + 'py_all_spikes' + str(motor_unit.motor_unit_number) + '.csv', header= False, index=False, na_rep='nan')
    
       


