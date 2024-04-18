#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""
import numpy as np
import numpy.typing as npt

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
        self.trigger_channel = 0
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
        
        # Find all MUAPs in channel with best signal


        return motor_unit