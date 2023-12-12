#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 14:57:12 2023

@author: Gabrielle
"""

import os
import intanutil.data as intan_data
import intanutil.header as intan_header
import pymicroemg.emg_recording as emg_recording

import matplotlib.pyplot as plt
import numpy as np

emg_dir = os.path.join('data', 'sample_data_20231124', 'real',
                       'Low quality', 'low amplitude- 20150324', 'raw')

#emg_header_file = os.path.join(emg_dir, 'info.rhd')


emg_files = emg_recording.EMGFiles(emg_dir)
emg_data = emg_files.load_emg_data()

#%%
"""
Notes
    
TODO: do we need info from any files besides the header (info.rhd) and amplifier .dat files?

"""