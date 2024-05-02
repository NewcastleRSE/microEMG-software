#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A class, EMGAnalysisReconstruct for localisation.

For use with preprocessed EMG data.

"""
from xml.etree.ElementInclude import include
import numpy as np
import numpy.typing as npt
import scipy.signal as sg
import scipy.optimize as opt
from scipy.linalg import toeplitz
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import cv2 
import os
import emg_analyser_python.emg_analyser_functions as tk
from emg_analyser_python.constants import QUICK_VERSION
from findpeaks import findpeaks
from pymicroemg.emg_data_preproc import EMGDataPreproc
import time

class EMGMotorUnit:
    """
    Class for storing motor unit data returned
    from reconstruction analysis

    """
    
    def __init__(
        self,
        loc
    ):
        """
        Initialise EMGMotorUnit object.

        Parameters
        ----------
        

        Returns
        -------
        None.

        """
        
        self.motor_unit_number = loc
        self.fibre_centres = np.array([])
        self.mean_spikes = np.array([])
        self.onsets = np.array([])
        self.all_spikes = np.array([])
        self.gn_potential = np.array([])
        
    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """
        
        ans = "EMG Motor Unit"
        ans += "\nMotor unit number: "
        ans += str(self.motor_unit_number)    
        ans += "\nFibre centres dimensions: "
        ans += str(self.fibre_centres.shape)
        ans += "\nMean spikes dimensions: "
        ans += str(self.mean_spikes.shape)
        ans += "\nOnsets dimensions: "
        ans += str(self.onsets.shape)
        ans += "\nAll spikes dimensions: "
        ans += str(self.all_spikes.shape)
        ans += "\nGN potential dimensions: "
        ans += str(self.gn_potential.shape)           
        
        ans += "\n"
        
        return ans
    
class EMGMotorUnits:
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
        
        self.motor_units = []
        
    def __str__(self):
        """
        Return a string for the object

        Returns
        -------
        String

        """
        
        ans = "EMG Motor Units"
        ans += "\nNumber of motor units: "
        ans += str(len(self.motor_units))     
        
        ans += "\n"
        
        return ans
        
        
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
        self.spike_dur = 20
        self.half_subsample_size = 200
        self.max_opt_iterations = 200
       

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
        ans += "\nSpike duration: "
        ans += str(self.spike_dur)
        ans += "\nSubsample size: "
        ans += str(self.half_subsample_size)
        ans += "\nMaximum optimisation steps: "
        ans += str(self.max_opt_iterations) 
        
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
        self.number_of_channels = self.emg_data_preproc.emg_ts.shape[0]
        
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
               
        # Set up vector for signal to noise ratios for each channel
        self.signal_noise_ratios = np.zeros(self.number_of_channels)
        
        for channel in range(self.number_of_channels):
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
        motor_units: MotorUnit

        """
        
        # Create motor unit object to store final results       
        returned_motor_units = EMGMotorUnits()
        
        # Order by highest Signal to Noise Ratio
        self.calculate_SNR_ranks() 
        
        print(self.signal_noise_ratios_ranks)
        print(self.signal_noise_ratios[self.signal_noise_ratios_ranks])
        
        #sampling_freq = self.emg_data_preproc.fs
        
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
        #used_data = self.emg_data_preproc.emg_ts[sig_ind, :]
        #print(used_data.shape)
        #indices, locs = tk.TK_filter(used_data, sampling_freq)         
        
        # Plot for testing purposes
        #self.plot_MUs(used_data, indices, locs)
        
        ########################
        if True:
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
            
            # Set all to non broken likeMATLAB analysis for this data
            self.emg_data_preproc.chan.analyse_chan = np.full(self.number_of_channels, True)
            
        ########################

        n_peaks = np.max(locs) + 1
        
        print("MUs found: " + str(np.max(locs) + 1) + " via channel: " + str(sig_ind))

        print(self.emg_data_preproc.preproc_settings)
        print("Good channels:")
        print(self.emg_data_preproc.chan.analyse_chan)
        
        print(self.emg_data_preproc.emg_ts.shape[1] - self.settings.half_subsample_size - 1 - 1)
       
        print(np.sum(locs == 0))
        print(np.sum(locs == 1))
        
        print("pre loop") 
        
        # Loop thro' moter units
        #range(max(locs))
        for loc_select in range(2):
            
            # Save the concurrent signal from all other channels for each spike
            all_spikes = np.zeros((len(indices[locs==loc_select]), self.settings.n_electrodes, self.settings.half_subsample_size * 2 + 1)) #401?
            all_onsets = indices[locs==loc_select]
    
            # Zero reused vars
            t = 0
            self.opr = []
    
            for sample in range(len(indices)):
                if locs[sample] == loc_select:
                    # exclude spikes right at the edge of the recording
                    
                    if indices[sample] < (self.settings.half_subsample_size + 1) or indices[sample] > (self.emg_data_preproc.emg_ts.shape[1] - self.settings.half_subsample_size - 1 - 1):
                        print("indices[sample]")
                        print(indices[sample])
                        continue 
                    
                    
                    for channel in range(self.settings.n_electrodes):
                        # Skip bad channels
                        if not self.emg_data_preproc.chan.analyse_chan[channel]:                            
                            continue
                        
                        #print(channel)
                        #print(int(indices[sample] - 200))
                        #print(int(indices[sample] + 200 + 1))
                        all_spikes[t, channel, :] = self.emg_data_preproc.emg_ts[channel,
                                                    int(indices[sample] - self.settings.half_subsample_size):int(indices[sample] + self.settings.half_subsample_size + 1)]
                    
                    t += 1
                
            
            print('MU' + str(loc_select) + ': firings: ' + str(t + 1))
            
            if self.settings.mavg_all:
                self.settings.mavg_length = all_spikes.shape[0] - 1
            elif t < self.settings.mavg_length:
                # if there aren't enough spikes to model the MU, skip it
                print('low number of firings found')
                continue
            
            if t < 2:
                continue
            
            mean_spikes = np.squeeze(np.mean(all_spikes, axis = 0))
            clusters = self.peak_group(np.max(mean_spikes, axis = 1))
            
            #for broken_index in range(len(settings.broken_channels))
            #    clusters{settings.broken_channels(broken_index)}=[];
            for channel in range(self.number_of_channels):
                # Empty bad channels
                if not self.emg_data_preproc.chan.analyse_chan[channel]: 
                    clusters[channel] = []


            ##Fibre location reconstruction
            #options = optimset('MaxIter',10000);
            #options = optimset('PlotFcns',@optimplotfval,'MaxIter',10000);
            ##disp(['- cluster no: ' num2str(max([clusters{:}]))])
            pos = np.zeros((0,2))
            onsets = np.array([])
            #found_index = 0
    
            if self.settings.localise_first:
                max_signal_id = 0
            else:
                max_signal_id = all_spikes.shape[0] - self.settings.mavg_length
       
    
            for signal_id in range(max_signal_id):
            
                if self.settings.localise_first:
                    sig = np.squeeze(all_spikes[signal_id:(signal_id + self.settings.mavg_length + 1), :, :])
                else:
                    sig = np.squeeze(np.mean(all_spikes[signal_id:(signal_id + self.settings.mavg_length + 1), :, :], axis = 0))
            
        
                sub_clusters = self.findpeaks_2d(sig, 0.15)
            
                if sub_clusters.shape[0] == 0:
                    continue
                      
                for sub_cluster_index in range(sub_clusters.shape[0]):
                    # Ensure we don't get spikes outside of recording duration
                    # (400 samples)
                    
                    time_peak = np.max(np.hstack((sub_clusters[sub_cluster_index, 0], self.settings.spike_dur + 1)))
                    time_peak = np.min(np.hstack((time_peak, self.settings.half_subsample_size * 2 - self.settings.spike_dur)))
                                   
                    # Get the mean spikes for the fibre peak amplitude
                    peak_electrode = sub_clusters[sub_cluster_index, 1]
                    peak_start = np.max(np.hstack((peak_electrode - 3, 0)))
                    peak_stop = np.min(np.hstack((peak_electrode + 3, self.settings.n_electrodes - 1)))
                
                    included_electrodes = np.arange(peak_start, peak_stop + 1, dtype = "int")
                    
                    # Remove bad channels                  
                    good_channels = np.arange(0, self.settings.n_electrodes, dtype = "int") * self.emg_data_preproc.chan.analyse_chan  
                    
                    #print(included_electrodes)
                    
                    included_electrodes = np.intersect1d(included_electrodes, good_channels)
                    
                    print(included_electrodes)
                    #print(good_channels)
                    
                    if included_electrodes.shape[0] == 0:
                        continue
                  
                    self.sn = (sig[included_electrodes, int(time_peak - self.settings.spike_dur):int(time_peak + self.settings.spike_dur + 1)]).T
                    
                    # Needle model pos in mm                    
                    self.needle = np.zeros((self.settings.n_electrodes, 2))
                    # the tip of the needle is assumed to be 1 mm far from the first electrode on the x axis
                    baseX = 0.8
                    for i in range(self.settings.n_electrodes):
                        # add interElectrodeDist
                        self.needle[i, 0] = baseX + self.settings.offset
                        self.needle[i, 1] = 0
                        baseX = self.needle[i, 0]
                    
                    # Scaling factor from mm to scaled AU
                    self.needle = self.needle * 4
                    x0 = self.needle[int(peak_electrode), :]
                    self.needle = self.needle[included_electrodes, :]
                    print(x0.shape)
                    ## Non-linear optimisation algorithm for fibre positioning
                    #pos[found_index, 0:1], fval, _ = fminsearch(@deconv_wrapper, x0, options)
                    t0 = time.time()
                    opt_paras, _, iters, fcalls, wflag  = opt.fmin(self.deconv_wrapper, x0 = x0, maxiter = self.settings.max_opt_iterations, full_output=True)#, disp = False)
                    t1 = time.time()

                    total = t1-t0
                    print("total Time = ")
                    print(total)
                    
                    print(opt_paras)
                    print(iters)
                    print(fcalls)
                    print(wflag)
                    print("\n")
                    #opt_paras = opt_paras[0]
                    #print(opt_paras.shape)
                    #print(opt_paras)
                    pos = np.vstack((pos, opt_paras))
                    
                    ## Exhaustive search is used when we don't want to use the non-linear search algorithm
                    # ie to demonstrate the variance at various putative fibre
                    # coordinates near to the electrode
                    #if self.settings.exhaustive == 1:
                    #    # Start with the position of the nearest electrode
                    #    x0=pos[found_index, 0:1]
                    #    p, errs = exhaustive_search(x0);
                    #    # Append the array of variances to the motor unit
                    #    motor_unit{loc_select}.err_curve{cluster_index}={errs};
                    #    motor_unit{loc_select}.err_locs{cluster_index}={p};
                
                    #pos[found_index, 0] = pos[found_index, 0]/4
             
                    onsets = np.append(onsets, all_onsets[signal_id])

                    #found_index = found_index + 1
            
            # End of signal_id loop
        
            pos[:, 0] = pos[:, 0]/4
            
            ## This is some optional pruning of unrealistic results for the localisation
            #if self.settings.prune:
            #    if (pos[cluster_index, 0] > self.settings.prune_xlim[1] or
            #       pos[cluster_index, 0] < self.settings.prune_xlim[0] or
            #       abs(pos(cluster_index,2)) > settings.prune_ylim(1)):
            #        pos = pos[cluster_index, :]
                
           
    
            ## Append the results to the motor unit object to return
            if pos.shape[0] > 0:
                motor_unit = EMGMotorUnit(loc_select)
                motor_unit.fibre_centres = pos
                motor_unit.mean_spikes = mean_spikes
                motor_unit.onsets=onsets
                motor_unit.all_spikes = all_spikes
                motor_unit.gn_potential = self.opr
                returned_motor_units.motor_units.append(motor_unit)
            
        
        return returned_motor_units
    

    def plot_MUs(self, used_data, indices, locs):
        """
        Plot MUs for testing purposes

        Parameters
        ----------
        Index : 1D numpy NDArray[int]
                Index of MUAPs clustered
        loc : 1D numpy NDArray[int]
                location of the MUAPs in the signal

        Returns
        -------
        None

        """
        
        no_MUs = np.max(locs) + 1
        xmax = len(used_data)
        ymin = np.min(used_data)
        ymax = np.max(used_data)
        
        plt.subplots(no_MUs, 1)
        
        # Loop thro' MUs
        for one_MU in range(no_MUs):
            # Plot subplot
            plt.subplot(no_MUs, 1, one_MU + 1)
            # Get subset for this MU
            subset_MU = (one_MU == locs)
            # Get index positions for this MU
            positions = indices[subset_MU]
            plt.plot(indices[subset_MU], used_data[positions], 'k-', linewidth=1)
            plt.xlim(0, xmax)
            plt.ylim(ymin, ymax)

        # Save the plot
        # Firstly ensure the execution path is the same as the file path       
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        #os.chdir(dname)
        
        # Save all images in the Images folder
        plt.savefig(os.path.join(dname, "MUs.png"), format = "png")
    
        # Close the plot
        plt.close()

       
    def find_peaks(self, data, distance = 1, min_peak_height = None):
        """
        Try to return as near as possible the same answer as findpeaks in MatLab if not QUICK VERSION
        """

        if QUICK_VERSION:
            peaks, _ = sg.find_peaks(data, height = min_peak_height, distance = distance)
            return peaks
        else:
            return tk.detect_peaks(data, mph = min_peak_height, mpd = distance)

    
    def peak_group(self, signal):
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
        """
         
        locs = self.find_peaks(signal, 4, np.max(signal)/3)
               
        # Create list of empty lists
        groups = [ [] for _ in range(len(signal)) ]
            
        for peak in range(len(locs)):                
            left_index = np.max([0, locs[peak] - 3])
            right_index = np.min([len(signal) - 1, locs[peak] + 3])
                
            for index in range(left_index, (right_index + 1)):                 
                groups[index].append(peak)
                          
        return groups
    

    def findpeaks_2d_package(self, image, threshold):
        """
        Finds local maxima of a 2-dimensional image area
        Dependent on findpeaks algorithm from findpeaks package
        See https://erdogant.github.io/findpeaks/pages/html/Topology.html
        Parameters
        ----------
        signal: 2D numpy NDArray[float, float]
                n*m array of signal data
        threshold: float
                cutoff for defining a peak
        Returns
        -------
        locs: 2D numpy NDArray[int, int]
            2D array of location of peaks
        """
        
        # Initialize
        fp = findpeaks(whitelist=['peak'])
      
        # apply threshold
        imageThres = image[image > threshold]
  
        # Fit topology method on the 2d-vector
        results = fp.fit(imageThres)['df']
        # The output contains multiple variables
        #print(results.keys())
        # dict_keys(['Xraw', 'Xproc', 'Xdetect', 'Xranked', 'persistence', 'groups0'])
        #print(results)
        #print(type(results))
        
        return np.array(results.loc[results['peak'], ['x', 'y']])


    def findpeaks_2d(self, sig, threshold):
        """
        Finds local maxima of a 2-dimensional image area
        Dependent on findpeaks algorithm from findpeaks package

        Parameters
        ----------
        signal: 2D numpy NDArray[float, float]
                n*m array of signal data
        threshold: float
                cutoff for defining a peak as a prop
        Returns
        -------
        locs: 2D numpy NDArray[int, int]
            2D array of location of peaks
        """
        
        base = sig
        # remove negative deflection to discount 'doubling peaks'
        # from negative initial deflection of SFAP
        base[base < 0] = 0 
                
        # Interpolate between the electrodes in order to make gaussian filter
        # have roughly equal effect on distance as time
        interp_n = 4 
        # Points to interpolate over
        Xi = np.arange(1, base.shape[0] + 1) * interp_n - 1 
        # Points to return after interpolation
        Xo = np.arange(interp_n - 1, Xi[-1] + 1)
        #print("findpeaks_2d")
        #print(Xi.shape)
        #print(base.shape)
        #print(Xo.shape)
        
        # Need a loop here as in Python the base must be 1D
        b = np.zeros((Xo.shape[0], base.shape[1]))
        for i in range(base.shape[1]):
            b[:, i] = np.interp(Xo, Xi, base[:, i]) #base is 2D ?? so not working
    
        #print(b.shape)
        sigma = 3
        im = np.abs(gaussian_filter(b, sigma, truncate=np.ceil(2*sigma)/sigma))   #imgaussfilt(b, 3))
        # tophat transform       
        # Applying the Top-Hat operation
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))  
        im2 = cv2.morphologyEx(im, cv2.MORPH_TOPHAT, kernel) 
        
        # Extract each blob
        # s=regionprops(im3,'Centroid','PixelIdxList');
        locs = np.array([])
        found = False
        parse_limit = 0
        
        while not found:
            parse_limit = parse_limit + 1
            locs = self.findpeaks_2d_package(im2, np.max(im2) * threshold)
            #locs = locs.reshape(-1, 2)
            
            if locs.shape[0] < 1:
                threshold = threshold - 0.02
            elif locs.shape[0] > 22:
                threshold = threshold + 0.02
            else:
                found = True
            
            if threshold <= 0.05 or threshold > 1 or parse_limit > 20:
                locs = []
                found = True
            
        if locs.shape[0] > 0:
            #Interpolated locs back to electrode indices
            locs[:, 1] = np.round((locs[:, 1] + 1)/interp_n - 1).astype(int) 
           
        return locs
    
    

    def deconv_wrapper(self, loc):
        """
        Deconvolution
        Now reconstruct without using gn!
        Calculate deconvolution for each channel in a 50x50 grid
        Region is 0-1000u (Y) and 100-500u (X)
        Error is abs mismatch across the reconstructions of 'gn'
        Calculated as the max variance across the centre of the 5 recontructions.
        This example is a blind hunt across 2500 locations near the needle.
        Here, cn is 400 samples long so that a Toeplitz matrix can be created.

        Parameters
        ----------
        loc
        
        Returns
        -------
        total_var: 
        """
          
        self.no_needle_channels = self.needle.shape[0]
        self.opr = np.zeros((self.settings.spike_dur*2 + 1, self.no_needle_channels))
       
        cn = self.calc_cn(loc[0], loc[1], self.settings.half_subsample_size * 2)
        for k in range(self.no_needle_channels):
             a = self.tconv(cn[:, k], self.sn[:,k], self.settings.spike_dur*2 + 1)            
             self.opr[:, k] = self.tconv(cn[:, k], self.sn[:,k], self.settings.spike_dur*2 + 1)
        
        total_var = -1/np.max(np.var(self.opr, axis = 1, ddof=1))
        
        return total_var
    

    def calc_cn(self, fbx, fby, isz):
        """
        Channel functions
        Generate 1/r conv functions for coords fbx,fby for each channel.

        Parameters
        ----------
        loc
        
        Returns
        -------
        fbx:
        
        fby:
       
        isz: 
        """
        
        cn = np.zeros((isz, self.no_needle_channels))
        for channel in range(self.no_needle_channels):
            for j in range(isz):
                dx = np.abs(fbx - self.needle[channel, 0])  # X offset
                dy = np.abs(fby - self.needle[channel, 1])  # Y offset of channel i
                dz = np.abs(j - isz/2)                       # Z distance along fibre
                cn[j, channel] = 1/np.sqrt(dx*dx + dy*dy + dz*dz)
            
        return cn
  

    def tconv(self, ifn, sig, isz):
        """
        Deconvolution method function
        Create a Toeplitz matrix using the trailing 200 samples of cn
        First row will have the maximum at index 0, 2nd at 1 .....
        Use a Parzen window on the signal. See FFT deconvolution as to why!
        Then deconvolve sig by solving least squares problem.

        Parameters
        ----------
        ifn:
    
        sig:
   
        isz:
        
        Returns
        -------
        rsl
        """
    
        wsig = sg.windows.parzen(isz) * sig
        start_pos = len(ifn) - isz - 1
        end_pos = len(ifn) - 1
        tpl = toeplitz(ifn[start_pos:end_pos])
    
        rsl = (np.linalg.lstsq(tpl, wsig))[0]
    
        return rsl

    
