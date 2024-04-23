#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""
import numpy as np
import numpy.typing as npt
import scipy.signal as sg
import emg_analyser_python.emg_analyser_functions as tk
from emg_analyser_python.constants import QUICK_VERSION

from pymicroemg.emg_data_preproc import EMGDataPreproc

class EMGMotorUnit:
    """
    Class for storing motor unit data returned from reconstruction analysis

    """
    
    def __init__(
        self                  
    ):
        """
        Initialise EMGMotorUnit object.

        Parameters
        ----------
        

        Returns
        -------
        None.

        """
         
class EMGAnalysisReconstructSettings:
    """
    Class for storing EMG Analysis reconstruct settings.

    """

    def __init__(self):
        """
        Initialise settings.

        Returns
        -------
        None.

        """

        # Default settings
        self.n_electrodes = 0
        self.trigger_channel = -1
        # set as bad channels in preprocessed data
        #self.broken_channels = []
        self.exhaustive = False
        self.offset = 0.3000
        self.prune = False
        self.prune_xlim = np.array([-0.5000, 19.2000, 0.5000])
        self.prune_ylim = np.array([-2, 2])
        self.mavg_length = 1
        self.mavg_all = False
        self.localise_first = False
       
    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """
        
        ans = "EMG Analysis Reconstruct Settings"
        ans += "\nNumber of electrodes: "
        ans += str(self.n_electrodes)    
        ans += "\nTrigger channel: "
        ans += str(self.trigger_channel)
        ans += "\nExhaustive: "
        ans += str(self.exhaustive)
        ans += "\nOffset: "
        ans += str(self.offset)
        ans += "\nPrune: "
        ans += str(self.prune)
        ans += "\nPrune x limits: "
        ans += str(self.prune_xlim)
        ans += "\nPrune y limits: "
        ans += str(self.prune_ylim)
        ans += "\nMoving average length: "
        ans += str(self.mavg_length)
        ans += "\nMoving average all: "
        ans += str(self.mavg_all)
        ans += "\nLocalise first: "
        ans += str(self.localise_first)      
        
        ans += "\n"
        
        return ans
            
class EMGAnalysisReconstruct:
    """
    Class for performing reconstruct analysis

    """

    def __init__(
        self,       
        emg_data_preproc: EMGDataPreproc, 
        settings: EMGAnalysisReconstructSettings
    ):
        """
        Initialise EMGAnalysisReconstruct object.

        Parameters
        ----------
        emg_data_preproc: EMGDataPreproc
            Preprocessed EMG time series data

        Returns
        -------
        None.

        """

        self.emg_data_preproc = emg_data_preproc
        self.settings = settings
        
        # SNRs: The SNR values for each channel
        self.signal_noise_ratios = []
        # ranks: The rank of each channel on highest SNR
        self.signal_noise_ratios_ranks = []
        
        
    def calculate_SNR_ranks(self):
        """
        Calculate the signal to noise ratios and rank them

        Parameters
        ----------
        

        Returns
        -------
        None

        """
        
        #sampling_freq = self.emg_data_preproc.fs
        
        number_of_channels = self.emg_data_preproc.emg_ts.shape[0]
        
        # Set up vector for signal to noise ratios for each channel
        self.signal_noise_ratios = np.zeros(number_of_channels)
        
        for channel in range(number_of_channels):
            # Skip "bad" channels
            if self.emg_data_preproc.chan.analyse_chan[channel]:                        
                temp = self.emg_data_preproc.emg_ts[channel, :]
                self.signal_noise_ratios[channel] = np.mean(temp[temp > 0])
                # SNRs(channel)=sfdr(signal(channel,:),Fs);          
          
            
        # Sort SNRs in decending order
        self.signal_noise_ratios_ranks = np.argsort(-self.signal_noise_ratios)
    
    def run_reconstruction(self):
        """
        Do the reconstruction analysis

        Parameters
        ----------


        Returns
        -------
        motor_unit: MotorUnit

        """
        
        # Create motor unit object to store final results       
        motor_unit = EMGMotorUnit()
        
        # Order by highest Signal to Noise Ratio
        self.calculate_SNR_ranks() 
        
        print(self.signal_noise_ratios_ranks)
        print(self.signal_noise_ratios[self.signal_noise_ratios_ranks])
        
        sampling_freq = self.emg_data_preproc.fs
        
        # Find all MUAPs in channel with best signal    
        if self.settings.trigger_channel >= 0:
            sig_ind = self.settings.trigger_channel
        else:
            if self.signal_noise_ratios[self.signal_noise_ratios_ranks[0]] > 0:
                sig_ind = self.signal_noise_ratios_ranks[0]
            else:
                raise Exception("Sorry, no channels with a calculable signal to noise ratio!")
            
        # Apply Multi-dimensional TK operator (Teager-Kaiser)
        # to return MUAPs in channel
        used_data = self.emg_data_preproc.emg_ts[sig_ind, :]
        print(used_data.shape)
        # indices, locs = tk.TK_filter(used_data, sampling_freq)         
        
        # load test data instead for dev
        import csv
        name = "nrajh" #
        
        # Importing csv module  
        filename = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\loc_test_data.csv'
        with open(filename, 'r') as x:
            locs = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        filename = 'C:\\Users\\' + name + '\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\index_test_data.csv'
        with open(filename, 'r') as x:
            indices = list(csv.reader(x, delimiter=",", quoting=csv.QUOTE_NONNUMERIC))

        locs = (np.array(locs)).flatten()
        indices = (np.array(indices)).flatten()
        indices = np.round(indices - 1)
        locs = np.round(locs - 1)
        
        n_peaks = np.max(locs) + 1
        
        print("MUs found: " + str(np.max(locs) + 1) + " via channel: " + str(sig_ind))

        print(self.emg_data_preproc.preproc_settings)
        
        #range(max(locs))
        for loc_select in range(2):
            
            # Save the concurrent signal from all other channels for each spike
            all_spikes = np.zeros(((indices[locs==loc_select]).shape[0], self.settings.n_electrodes, 401)) #401?
            all_onsets = indices[locs==loc_select]
    
            # Zero reused vars
            t = 0
            opr = []
    
            for sample in range(indices.shape[0]):
                if locs[sample] == loc_select:
                    # exclude spikes right at the edge of the recording
                    if indices[sample] < 201 or indices[sample] > self.emg_data_preproc.emg_ts.shape[1] - 201 - 1:
                        continue 
                    
                    
                    for channel in range(self.settings.n_electrodes):
                        # Skip bad channels
                        if not self.emg_data_preproc.chan.analyse_chan[channel]:
                            print("bad")
                            print(channel)
                            continue
                        
                        #print(channel)
                        #print(int(indices[sample] - 200))
                        #print(int(indices[sample] + 200 + 1))
                        all_spikes[t, channel, :] = self.emg_data_preproc.emg_ts[channel, int(indices[sample] - 200):int(indices[sample] + 200 + 1)]
                    
                    t += 1
                
            
            print('MU' + str(loc_select) + ': firings: ' + str(t))
            
            if self.settings.mavg_all:
                self.settings.mavg_length = all_spikes.shape[0] - 1
            elif t < self.settings.mavg_length:
                # if there aren't enough spikes to model the MU, skip it
                print('low number of firings found')
                continue
            
            if t < 2:
                continue
            
            #mean_spikes = np.squeeze(np.mean(all_spikes, axis = 0))
            #clusters, _ = self.peak_group(np.max(mean_spikes, axis = 1))
            
            #for broken_index in range(len(settings.broken_channels))
            #    clusters{settings.broken_channels(broken_index)}=[];
            
    


        return motor_unit
    

    def find_peaks(data, distance = 1, min_peak_height = None):
        """
        Try to return as near as possible the same answer as findpeaks in MatLab
        """

        if QUICK_VERSION:
            peaks, _ = sg.find_peaks(data, height = min_peak_height, distance = distance)
            return peaks
        else:
            return tk.detect_peaks(data, mph = min_peak_height, mpd = distance)

    
    def peak_group(signal):
        """
        Function to group electrodes by related signal
        Identifies peaks in the signal, and then adjacent rows are assigned into
        groups related to that signal.

        Parameters
        ----------
        signal: 1D numpy NDArray[float], for example the SNRs across the electrodes


        Returns
        -------
        groups: 1D numpy NDArray[int]
            array of integers & zeros reflecting the signal groups that
            the electrodes are placed into
        locs: 1D numpy NDArray[int]
            List of peak indices found
        """
         
        locs = self.find_peaks(signal, 4, np.max(signal)/3)
               
        groups = np.array((1, len(signal)))
            
        for peak in range(len(locs)):                
            left_index = np.max([1, locs[peak] - 3])
            right_index = np.min([len(signal), locs[peak] + 3])
                
            for index in range(left_index, (right_index + 1)):
                groups[index] = [groups[index], peak]
                
            
        return groups, locs