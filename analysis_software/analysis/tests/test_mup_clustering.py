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
import json 
import pandas as pd

from pymicroemg.emg_data_preproc import EMGDataPreproc
from pymicroemg.emg_files import EMGFiles
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_data import EMGData

from pymicroemg.emg_reconstruct_settings import EMGAnalysisReconstructSettings
from pymicroemg.emg_reconstruct_settings import EMGAnalysisMotorUnitSettings
from pymicroemg.emg_reconstruct import EMGAnalysisReconstruct
from pymicroemg.emg_motor_unit import EMGMotorUnit

name = "richa" #"nrajh" #"nrajh" #
        
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

mu_settings = EMGAnalysisMotorUnitSettings()

# Set the number of electrodes, same as the number of channels?
analysis_settings.n_electrodes = emg_data_preproc.emg_ts.shape[0]

print(analysis_settings)

print("Processed data shape: ")
print(emg_data_preproc.emg_ts.shape)

import time

t0 = time.time()

reconstruct = EMGAnalysisReconstruct(emg_data_preproc, mu_settings, analysis_settings)

t0 = time.time()
#print("Loading test data...\n")
#Set same data as MATLAB for testing...
#filename = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\processed_multi_emg_matlab.csv'
#reconstruct.load_data(filename)

t1 = time.time()
total = t1-t0
print("Time = ")
print(total)

print("Finding motor units...\n")
print(mu_settings)
reconstruct.find_motor_units()


t2 = time.time()
total = t2-t1
print("Time = ")
print(total)

#input("Stop...")

#filename_locs = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\loc_test_data.csv'
#filename_indices = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\index_test_data.csv'
#reconstruct.load_motor_unit_data_from_matlab(filename_indices, filename_locs)


motor_unit_number = 0
print("Reconstructing fibres for MU " + str(motor_unit_number) + "...\n")

reconstruct.reconstruct_fibres(motor_unit_number)

# output onsets and fibre centres
filename_onsets = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_onsets_'+ str(motor_unit_number) +'.csv'
filename_fibre_centres = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_fib_centres_'+ str(motor_unit_number) +'.csv'
motor_unit = reconstruct.found_motor_units.motor_units[motor_unit_number]

df = pd.DataFrame(motor_unit.onsets) 
# save the dataframe as a csv file 
df.to_csv(filename_onsets, header= False, index=False, na_rep='nan')

# convert array into dataframe
df = pd.DataFrame(motor_unit.fibre_centres) 
# save the dataframe as a csv file 
df.to_csv(filename_fibre_centres, header = False, index=False, na_rep='nan')


t3 = time.time()
total = t3-t2
print("Time = ")
print(total)


#print("Loading MUP MATLAB data")
#filename_fibre_centres = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\fibre_centres' + str(motor_unit_number+1) + '.csv'
#filename_onsets = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\onsets' + str(motor_unit_number+1) + '.csv'
#reconstruct.load_mup_data_from_matlab(motor_unit_number, filename_fibre_centres, filename_onsets)


#print("Loading MUP py data")
#filename_onsets = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_onsets_X1.csv'
#filename_fibre_centres = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_fib_centres_X1.csv'
#reconstruct.load_mup_data(motor_unit_number, filename_fibre_centres, filename_onsets)


all_motor_units = reconstruct.found_motor_units


# Do k-means clustering
print("Clustering motor unit potentials using k-means clustering")
all_motor_units.cluster_fibre_potentials(motor_unit_number, 0)

motor_unit = all_motor_units.motor_units[motor_unit_number]

# Write results  

filename_clusters = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_kmean_clusters' + str(motor_unit_number) + '.csv' 
filename_centres = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_kmean_centres' + str(motor_unit_number) + '.csv' 
filename_locs = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_kmean_locs' + str(motor_unit_number) + '.csv' 
  
print(motor_unit.fibre_clustering_results.keys())
# convert array into dataframe 
df = pd.DataFrame(motor_unit.fibre_clustering_results["fibre_clusters"]) 
# save the dataframe as a csv file 
df.to_csv(filename_clusters, header= False, index=False, na_rep='nan')

# convert array into dataframe
df = pd.DataFrame(motor_unit.fibre_clustering_results["fibre_centres_median"]) 
# save the dataframe as a csv file 
df.to_csv(filename_centres, header = False, index=False, na_rep='nan')

# convert array into dataframe 
#df = pd.DataFrame(motor_unit.fibre_clustering_results["mup_fibre_pos"]) 
# save the dataframe as a csv file 
#df.to_csv(filename_locs, header= False, index=False, na_rep='nan')

# convert array into dataframe 
#df = pd.DataFrame(motor_unit.fibre_clustering_results["fibre_centres_median"]) 
# save the dataframe as a csv file 
#df.to_csv(filename_centres)

#Plot clustering results
all_motor_units.plot_fibre_potential_clustering_one_motor_unit(motor_unit_number)
plt.show()

t4 = time.time()
total = t4-t3
print("Time = ")
print(total)

# To separate different test output
#extra_label = "_filters3_" #"_highest3_" #"_filters2_" # "_highest2_" #"_filters_"

tX = time.time()

total = tX-t0

print("Total Time =")
print(total)



