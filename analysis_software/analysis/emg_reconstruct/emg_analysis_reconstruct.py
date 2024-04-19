#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""
import numpy as np
import numpy.typing as npt
import emg_analyser_python.emg_analyser_functions as tk

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
        indices, locs = tk.TK_filter(used_data, sampling_freq)         
        n_peaks = max(locs)
        
 
      
        print("MUs found: " + str(max(locs)) + " via channel: " + str(sig_ind))

        #range(max(locs))
        for loc_select in range(2):
            
            # Save the concurrent signal from all other channels for each spike
            all_spikes = np.zeros(((indices[locs==loc_select]).shape[0], self.settings.n_electrodes, 401)) #401?
            all_onsets = indices[locs==loc_select]
    
            # Zero reused vars
            t = 1
            opr = []
    
            for sample in range(indices.shape[0]):
                if locs[sample] == loc_select:
                    # exclude spikes right at the edge of the recording
                    if indices[sample] < 201 or indices[sample] > self.emg_data_preproc.emg_ts.shape[1] - 201:
                        continue 
                    
                    
                    for channel in range(self.settings.n_electrodes):
                        # Skip bad channels
                        if not self.emg_data_preproc.chan.analyse_chan[channel]:
                            continue
                        
                        all_spikes[t, channel, :] = self.emg_data_preproc.emg_ts[channel, indices[sample] - 200:indices[sample] + 200]
                    
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
            



        return motor_unit