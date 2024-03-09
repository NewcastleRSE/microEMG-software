import numpy as np
import scipy.signal as sg

"""
These functions are reimplemented in Python by Richard Howey
2024, RSE team, Newcastle University
Comment largely taken from original code.
If a function had no comments originally then it may not in the translated version also.
Original Comments below:

Algorithm is based on the following paper :
H. Sedghamiz and Daniele Santonocito,'Unsupervised Detection and
Classification of Motor Unit Action Potentials in Intramuscular
Electromyography Signals', The 5th IEEE International Conference on
E-Health and Bioengineering - EHB 2015, At Iasi-Romania.
Author:
Hooman Sedghamiz
June 2015, Linkoping University
Please cite the paper if any of the methods were helpful
"""

def running_TEO(raw_signal, k = 1):
    """
    calcs the function x(n)^2 - x(n-k)*x(n+k)

    this is the standard energy operator (TEO)
    some people like to invent new names for old concepts and call this "NEO -> nonlinear energy operator"

    Parameters
    ----------
    raw_signal : 1D numpy NDArray[float]
    k : integer

    Returns
    -------
    1D numpy NDArray[float]

    """

    # Final result
    return raw_signal**2 - np.concatenate(
        (raw_signal[k:], np.zeros(k))
    ) * np.concatenate((np.zeros(k), raw_signal[:-k]))


def MTEO(raw_signal, ks, filter = True):
    """
    
    Parameters
    ----------
    raw_signal : 1D numpy NDArray[float]
        signal
    ks : 1D numpy NDArray[int]
        levels of MTEO
    filter : boolean
        Filter flag
        
    Returns
    -------
    runTEO : 1D numpy NDArray[float]
    tmp : 1D numpy NDArray[float] 
    """ 
    
    L = len(ks)    
    tmp = np.zeros((L, len(raw_signal)))
    v = np.zeros(L)

    for i in range(L):
        tmp[i, :] = running_TEO(raw_signal, ks[i])
       
        # Filter flag
        if filter:
            # ensure the sample variance is used and not the population variance by setting ddof = 1
            v[i] = np.var(tmp[i, :], ddof=1) 
          
            # apply the window
            win = np.hamming(4 * ks[i] + 1)
           
            tmp[i, :] = sg.filtfilt(win, 1, tmp[i, :]) / (v[i])  # def was v unsquared
            

    if L > 1:
        runTEO = sum(tmp)  # runTEO + tmp./v(i);
        # runTEO = max(tmp);
    else:
        runTEO = tmp[i, :]

    return runTEO, tmp



def PsC(template, sig, lag = None):
    """    
    Psuedo_Correlation
    Computes the Pseudo Correlation, a finer approach than normal
    correlation for template matching. Please review the paper below in order
    to see why it is much more accurate for the pattern recognition
    
    Parameters
    ----------
    template : 1D numpy NDArray[float, float]
        Storing templates
    sig: 1D numpy NDArray[float]
        the signal that we are searching the template in
    lag : integer
        does PsC for the lag between -lag : lag, it should be in samples,
        for example half the length of the input signal
        
    Returns
    -------
    PsC_score : float
        maximum score at best lag
    best_lag : int
        best lag
    """

    if lag is None:
        lag = round(len(sig)*0.5)
    
    m = len(template)
    n = len(sig)

    if m > n:
        raise Exception('Length of Template should be equal or smaller than pattern') 
   
    sig = np.hstack((np.zeros((lag)), sig, np.zeros((2 * lag))))
    
    p4 = np.zeros(m)
    normaliz = np.zeros(m)
    PsC_score = np.zeros(n);
 
    for k in range(2 * lag + 1):
        for i in range(m):
            p1 = template[i] * sig[k + i]
            p2 = abs(template[i] - sig[k + i])
            p3 = max(abs(template[i]), abs(sig[k + i]))
            p4[i] = (p1 - p2*p3)
            normaliz[i] = p3**2
         
        PsC_score[k] = max(sum(p4)/sum(normaliz), 0)     

    best_lag = np.argmax(PsC_score)
    PsC_s = PsC_score[best_lag]
    best_lag = best_lag - lag
    
    return PsC_s, best_lag


def find_spikes(templates, sigs, locs, sampling_freq, threshold):
    """
    Uses Psuedo Correlation for spike Classification
    NOTE: USES PsC_Mex for fast clustering

    Parameters
    ----------
    template : 2D numpy NDArray[float, float]
        Storing templates
    sigs : 2D numpy NDArray[float, float]
        signal, each row a separate channel
    locs : 1D numpy NDArray[int]
        locations
    sampling_freq : float
        Sampling frequency
    threshold : float
        threshold    
        
    Returns
    -------
    loc : 1D numpy NDArray[int]
        location of the spikes in the signal
    new_sigs : 2D numpy NDArray[float, float]
        new signal
        
    """ 
 
    spike_locs = np.full(len(locs), False)
    #lag (def was 0.0002)
    lag = round(0.0002 * sampling_freq) 

    for i in range(len(locs)):
        tmp = sigs[i, :]
        PsC_s, _ = PsC(templates, tmp, lag)
        if PsC_s >= threshold:
            spike_locs[i] = True
            sigs[i, :] = sigs[i, :] - templates
        
    new_sigs = sigs
    
    return spike_locs, new_sigs


def resolve_peaks(sig, decision_thres, sampling_freq):
    """
    Resolves the spikes which are too close

    Parameters
    ----------
    sig : 1D numpy NDArray[int]
        signal
    decision_thres : float 
        Decision threshold
    sampling_freq : float
        Sampling frequency
        
    Returns
    -------
    TE : 1D numpy NDArray[float]
        Detected Muaps 
    """ 

    sig = np.abs(sig)
    # def 15 millisec min distance
    min_pd = max(1, np.round(0.0015 * sampling_freq))
    tmp = np.zeros(len(sig))
    ind = (sig > decision_thres)
    tmp[ind] = sig[ind]
    TE, _ = sg.find_peaks(tmp, distance = min_pd)
       
    return TE

def MTH(MTEO, ks, L, sampling_freq):
    """
    Multi-Scale Thresholding

    this is the standard energy operator (TEO)
    some people like to invent new names for old concepts and call this "NEO -> nonlinear energy operator"

    Parameters
    ----------
    MTEO : 1D numpy NDArray[float]
        MTEO signal outputs from MTEO function    
    ks : int
        level of MTEO
    L : int
        is the factor that multiplies [cost of comission]/[cost of omission].
        For most practical purposes -0.2 <= L <= 0.2. Larger L --> omissions
        likely, smaller L --> false positives likely. For unsupervised
        detection, the suggested value of L is close to 0.
    sampling_freq : float
        Sampling frequency
        
    Returns
    -------
    TE : 1D numpy NDArray[float]
        Detected Muaps
    decision_thres : float 
        Decision threshold
    """
    
    M = len(MTEO)
    ks = ks*2

    # define detection parameter
    # log(Lcom/Lom), where the ratio is the maximum 
    Lmax = -551.0520      
    L = L * Lmax
  
    # take only coefficients that are independent (W(i) apart) for median
    # standard deviation    
    Sigmaj = np.median(np.abs(MTEO[::np.round(ks)] - np.mean(MTEO)))/0.6745
    #hard threshold
    Thj = Sigmaj * np.sqrt(2 * np.log(M))  
    indexes = (np.abs(MTEO) > Thj)
      
    if len(indexes) > 0:
        sig_out = MTEO[indexes]    
        # mean of the signal coefficients
        Mj = np.mean(np.abs(sig_out))
        # prior of spikes
        PS = len(sig_out)/M
        # prior of noise
        PN = 1 - PS
        # decision threshold
        decision_thres = Mj/2 + (Sigmaj**2)/Mj * (L + np.log(PN/PS))
        # make decision_thres>=0
        decision_thres = np.abs(decision_thres) * (decision_thres >= 0)         
        TE = resolve_peaks(MTEO[:], decision_thres, sampling_freq)
    else:
        
        Mj = Thj;
        # assume at least one spike
        PS = 1/M
        PN = 1 - PS
        # decision threshold
        decision_thres = Mj/2 + Sigmaj^2/Mj * (L + np.log(PN/PS))
        # make decision_thres>=0
        decision_thres = np.abs(decision_thres)* (decision_thres >= 0)
        ind  = np.abs(MTEO) > decision_thres
        ind = MTEO[ind]
        if np.empty(ind):
            # do nothing ct=[0];
            TE = []
        else:
            # This function resolves too close peaks
            TE = resolve_peaks(MTEO, decision_thres, sampling_freq)
                           
    
    # to enhance performance discard detections more than 700Hz period
    if len(TE) > 0:
        if (len(TE)/(len(MTEO)/sampling_freq)) > 500 or (len(TE)/(len(MTEO)/sampling_freq)) < 1:
            TE = []
            decision_thres = []            
 
    return TE, decision_thres

def spike_separator(S_block, template, S_neighbor, window, threshold):
    """       
    Divides the Spike in two sections
    Removes the second pulse superimposed if it is far enough from another 
    Spike
    
    Parameters
    ----------
    S_block : 2D numpy NDArray[float, float]
        Store METO templates    
    template : 2D numpy NDArray[float, float]
        Storing templates
    S_neighbor : integer
        Search Neighborhood window size
    window : integer
        Window to separate spikes
    threshold : float
        threshold
         
    Returns
    -------
    S_block : 2D numpy NDArray[float, float]
        Store METO templates
    template : 2D numpy NDArray[float, float]
        Storing templates
    """
 
    # First Part
    maxima_1, _ = sg.find_peaks(S_block[0, :S_neighbor])
    
    if len(maxima_1) > 0:
        amp_M1 = S_block[0, maxima_1]
        dist_m = (S_neighbor - (maxima_1 + 1)) >= window
        dist_a = (amp_M1 >= threshold)
        maxima_1 = maxima_1[dist_m & dist_a]
        
        if len(maxima_1) > 0:
            #closest to peak
            maxima_1 = maxima_1[0]       
            inverted = 1.01 * max(S_block[0, maxima_1:S_neighbor]) - S_block[0, maxima_1:S_neighbor]
            minima_1, _ = sg.find_peaks(inverted)
            
            if len(minima_1) > 0:
                minima_1 = minima_1[0]
                minima_1 = maxima_1 + minima_1
                # make the uncorrelated zero
                S_block[0, :minima_1] = 0 
                template[0, :minima_1] = 0
                
        else:
            #do nothing
            S_block[0, :] = S_block[0, :] 
            template[0, :] = template[0, :]
                   
    else:
        S_block[0, :] = S_block[0, :]
        template[0, :] = template[0, :]
         
       
    ## 2nd Part       
    maxima_2, _ = sg.find_peaks(S_block[0, S_neighbor:])
    
    if len(maxima_2) > 0:
        amp_M2 = S_block[0, maxima_2]
        dist_m = (maxima_2 + 1 >= window)
        dist_a = (amp_M2 >= threshold)
        maxima_2 = maxima_2[dist_m & dist_a]
         
        if len(maxima_2) > 0:
            #closest to peak
            maxima_2 = maxima_2[0]
            
            end_pos = (S_neighbor + maxima_2 + 1)
            if end_pos > S_block.shape[1]:
                end_pos = S_block.shape[1]
                
            inverted = 1.01 * max(S_block[0, S_neighbor:end_pos]) - S_block[0, S_neighbor:end_pos]
            
            minima_2, _ = sg.find_peaks(inverted)
            
            if len(minima_2) > 0:
                minima_2 = minima_2[-1]
                minima_2 = S_neighbor - minima_2
                # make the uncorrelated zero 
                start_pos = (S_block.shape[1] - 1 - minima_2)
                if start_pos < 0:
                    start_pos = 0
                
                #Should be like this? Did as MatLab above.
                #minima_2 = minima_2[-1]
                #minima_2 = minima_2 + S_neighbor
                #if start_pos >= S_block.shape[1]:
                #    start_pos = S_block.shape[1] - 1
             
                S_block[0, start_pos:] = 0 
                template[0, start_pos:] = 0
               
        else:
            S_block[0, :] = S_block[0, :]
            template[0, :] = template[0, :]      
        
    else:
        S_block[0, :] = S_block[0, :]
        template[0, :] = template[0, :]
       
    return S_block, template

def border_detector(S_block, template, threshold, threshold1):
    """       
    This function Assigns a label to each template  
    
    Parameters
    ----------
    S_block : 1D numpy NDArray[float]
        Store METO template    
    template : 1D numpy NDArray[float]
        Storing a template
    threshold : float
        threshold
    threshold1 : float
        threshold  
        
    Returns
    -------
    features : 1D numpy NDArray[float]
        features of data
       
    """ 
    
    maxima_1, _ = sg.find_peaks(S_block);
    amp_M1 = S_block[maxima_1]
    
    A = amp_M1 > threshold
    # Logical Indexing
    B = maxima_1[A]
    
    if len(B) > 5:
        B = B[0:5]
    
    tmp = np.zeros((2*len(B), 2))
    D_border = np.zeros(len(B))
    features = np.full(24, np.NaN)
 
    # compute features related to exterema (limited to 3 for now)
    for i in range(len(B)):                   
        # (limited to 5 turns or maximas)
        if i < 5:  
            dummy = np.argwhere(S_block[:B[i]] <= threshold1)
     
            if len(dummy) == 0:
                tmp[i, 0] = np.argmin(S_block[:B[i]])    
            else:
                tmp[i, 0] = dummy[-1]
                
            tmp[i, 0] = B[i] - tmp[i, 0]
     
            dummy = np.argwhere(S_block[B[i]:] <= threshold1)
     
            if len(dummy) == 0:
                tmp[i, 1] = np.argmin(S_block[B[i]:])     
            else:
                tmp[i, 1] = dummy[0]
            
            D_border[i] = tmp[i, 0] + tmp[i, 1]

    # See if the peak is a maxima or minima
    #amp = amp_M1(A);
    amp = S_block[B]
    for i in range(len(B)):
        if template[B[i]] < 0:
            # 1 shows a minima
            amp[i] = 1;                               
        else:
            # 2 shows a maxima
            amp[i] = 2;                               
      
    # number of local Max (0 - 4)
    features[0:len(amp)] = amp;       
    # approximate period (5 - 9)
    features[5:(5 + len(D_border))] = D_border + 1
    # time difference between each maxima(10 - 13)
    features[10:(10 + len(np.diff(B)))] = np.diff(B)
    # Amp of Exterma(14 - 18)
    features[14:(14 + len(amp))] = S_block[B]
    # Phase of maximas(19 - 23)
    features[19:(19 + len(amp))] = B + 1  
    # Integral of M_TEO
    #features(1,25) = sum(S_block);
    # RMS of the template                  
    #features(1,26) = rms(S_block);                 

    return features

def initialize(sig): 
    """    
    Initialize the signal with filters.
    
    Parameters
    ----------
    Sig : 1D numpy NDArray[float]
        EMG signal Vector
    sampling_freq : float
        Sampling Frequency (e.g. 2000 Hz)
    notch : boolean
        Flag for whether to do the notch filter or not
         
    Returns
    -------
    Sig : 1D numpy NDArray[float]
        Filtered EMG signal Vector
    """
  
    ## Initialzie
    # Remove the baseline shift
    sig = sg.detrend(sig)
    # Remove mean
    sig = sig - np.mean(sig) 
    # Normalize st. deviation
    sig = sig/np.std(sig, ddof = 1)                    

    # Commented out as considered redundant by earlier filters, was:
    # initialize(sig, sampling_freq, notch = False) 
    '''
    ## Notch Filter
    if notch:
        # Original MatLab
        # d = designfilt('bandstopiir','FilterOrder',32,
        # 'HalfPowerFrequency1',59,'HalfPowerFrequency2',61, 'DesignMethod','butter','SampleRate',sampling_freq)
        # sig = sg.filtfilt(d, sig)

        # Frequency to be removed from signal (Hz)
        f0 = 60.0
        # Quality factor
        Q = 30.0  
        b_notch, a_notch = sg.iirnotch(f0, Q, fs = sampling_freq)
        
        # Apply notch filter to the noisy signal using signal.filtfilt
        sig = sg.filtfilt(b_notch, a_notch, sig)
    

    ## High-Pass Filter
    # Normalized cutoff frequency
    F_l = 50/(sampling_freq/2)                         
    F_h = 1000/(sampling_freq/2)
    Wn = [F_l, F_h]
    # Butterworth filter
    z, p, k = sg.butter(4, Wn)  
    # Convert to SOS form
    sos = sg.zpk2sos(z, p, k)              
    sig = sg.sosfiltfilt(sos, sig)
    '''
    
    return sig

def linear_map(X, original_range, map_range):
    """    
    Linearly Maps a set of numbers to another scale
    
    Parameters
    ----------
    X : 1D numpy NDArray[float]
        The number to be mapped
    original_range : 1D numpy NDArray[float]
        The original range of the variable e.g. ([0 10]), the
        minimum and maximum possible value that X can take
    map_range : 1D numpy NDArray[float]
        The new min and maximum range that the number should be
        assigned to that range
   
    Returns
    -------
    Y : integer
        Mapped number
    """

    a1 = original_range[0]
    a2 = original_range[1]

    b1 = map_range[0]
    b2 = map_range[1]

    if original_range[0] != original_range[1]:
        Y = b1 + ((np.asarray(X) - a1) * (b2 - b1)) / (a2 - a1)
    else:
        Y = np.asarray(X)/original_range[0]
    
    # map to nearest integer
    return np.round(Y)                     

def generate_titles(features):
    """    
    Title Generation:
    Generates the titles and also initial set of clusters based on label matching 
    
    Parameters
    ----------
    features : 2D numpy NDArray[float, float]
        As returned by border_detector
    Returns
    -------
    title : 1D numpy NDArray[int]
        List of integers labelling each list of features.
        Considered the same if first 5 numbers are the same and the other numbers are the same or differ by exactly 1
    """
    
    no_features = features.shape[0]
    
    if no_features == 0:
        return []
        
    # Label first list of features as "1"
    titles = np.zeros(no_features) 
    title_counter = 1
    titles[0] = title_counter
    # Current list of feature groups to check if a list of features belongs to it
    features_to_check = [0]
    
    for i in range(1, no_features):        
        for j in features_to_check:            
            # Check if the first 5 elements are the same
            if (features[j, :5] == features[i, :5]).all():
                # Check if remaining elements are the same or differ by exactly 1
                diff = np.abs(features[j, 5:] - features[i, 5:])
                if ((diff == 0) | (diff == 1)).all():
                    # Considered the same, so give the same title
                    titles[i] = titles[j]                    
                    break
        
        # Does not match any previous feature groups so give a new "title"
        if titles[i] == 0:
            title_counter += 1
            titles[i] = title_counter
            features_to_check.append(i)
            
    return titles


def merge_clusters(template, titles, threshold, sampling_freq, sig_len):
    """    
    This function uses Pysuedo-Correlation for clustering method
    Checks first for inter-cluster similarity and then for clusters
    themself that are similar
    
    Parameters
    ----------
    template : 2D numpy NDArray[float, float]
        Storing templates
    title : 1D numpy NDArray[int]
        List of integers labelling each list of features.
    threshold : float
        threshold
    sampling_freq : float
        Sampling Frequency (e.g. 2000 Hz)
    sig_len : integer
        length of signal
        
    Returns
    -------
    uniq_c : integer
        Mapped number
    """
    
    no_unique_titles = int(max(titles))
    c = 0
    semi_final = np.zeros((no_unique_titles, template.shape[1]))
    counter = np.full(no_unique_titles, False)

    if round(sig_len/sampling_freq) < 10:
        #minimum length of clusters
        min_l = np.ceil(sig_len/sampling_freq)            
    else:
        min_l = 3
    
    #lag(def 0.0002)
    lag = round(0.0002*sampling_freq)                       
    
    # Checking for inter-cluster similarity
    for tit in range(1, no_unique_titles + 1):
        A = (titles == tit)
        tmp_t2 = template[A, :] 
        
        if tmp_t2.shape[0] >= min_l:
            semi_final[c, :] = np.median(tmp_t2, axis = 0)
            
            for j in range(tmp_t2.shape[0]):             
                PsC_s, _ = PsC(semi_final[c, :], tmp_t2[j, :], 4)
               
                if PsC_s < threshold:
                    tmp_t2[j, :] = np.NaN
                              
            tmp_t2 = tmp_t2[np.isfinite(tmp_t2[:, 0]), :]
            
            if tmp_t2.shape[0] < min_l:
                semi_final[c, :] = np.NaN
                counter[c] = False     
            else:
                semi_final[c, :] = np.median(tmp_t2, axis = 0)
                counter[c] = True
          
            c = c + 1
     
    # Now merging clusters that are similar
    semi_final = semi_final[counter, :]

    for i in range(semi_final.shape[0]):
        if (~np.isnan(semi_final[i, :])).all():
            for j in range(semi_final.shape[0]):
                if i != j and (np.isnan(semi_final[j, :])).all():
                    PsC_s, _ = PsC(semi_final[i, :], semi_final[j, :], lag)
                    if PsC_s > threshold:
                        semi_final[i, :] = (semi_final[i, :] + semi_final[j, :]) * 0.5
                        semi_final[j, :] = np.NaN
               
    uniq_c = semi_final[np.isfinite(semi_final[:, 1]), :]

    return uniq_c


def TK_filter(sig, sampling_freq, C = 0.1, threshold_PsC = 0.1, init = True, wind = 0.020):
    """    
    Function for Spike detection and Classification
    This is designed to filter out shallow peaks out of Action potentials
    with the help of Multi-dimensional TK operator (Teager-Kaiser). The function has several
    subroutins and uses template and label matching in order to cluster the
    action potentials in the signal.
    
    Parameters
    ----------
    sig : 1D numpy NDArray[float]
        EMG signal Vector
    sampling_freq : float
        Sampling Frequency (e.g. 2000 Hz)
        average number of samples obtained in one second
    C : float
        Threshold for the Spike Detection.
        Default 0.6*STD(0.8-1.2)
    threshold_PsC : float
        Correlation Threshold, two templates are clustered in the same
        basket if their correlation score goes higher than this value
    init : boolean
        Flag for filtering, leave it empty if you have no idea what this is
    wind : float
        Windows length for storing the templates, it is an important factor
        for the analysis, so leave it empty if you have no idea about it.    
        
    Returns
    -------
    Index :
        Index of MUAPs clustered
    loc :
        location of the MUAPs in the signal
    """
   
    ## Initialzie and highpass filter
    # Detrends and band-pass filters the signal
    if init:
        sig = initialize(sig) #, sampling_freq, True)
    
    ## upsampling for better accuracy in Classification

    upsample_flag = 0
    
    if sampling_freq < 10000 and sampling_freq > 4000:
        # upsample by a factor of 5
        sig = sg.resample_poly(sig, 5, 1)  
        sampling_freq = 5 * sampling_freq
        upsample_flag = 5
    elif sampling_freq > 10000 and sampling_freq < 15000:
        # upsample by a factor of 2 
        sig = sg.resample_poly(sig, 2, 1)
        sampling_freq = 2 * sampling_freq
        upsample_flag = 2
    elif sampling_freq <= 3000:
        sig = sg.resample_poly(sig, 8, 1)
        sampling_freq = 8 * sampling_freq
        upsample_flag = 8
    
    Index = []
    loc = []
   
    ## MTEO
    # Scales for MTEO (or 1,3,5) detection
    ks = [2, 3, 5]                   
    if upsample_flag > 0:
        ks = ks * 2                   
    
    ## First Stage Spike detection
    # Compute MTEO
    sig_TEO = MTEO(sig, ks)               
    locs, threshold = MTH(sig_TEO, ks, C, sampling_freq)

    # Removing those peaks on begining and end of sig
    # Minus 1, as Python indexes start at 0
    A = locs > round((wind)*sampling_freq) - 1
    locs = locs[A]
    B = locs < (len(sig) - round((wind)*sampling_freq) - 1)
    locs = locs[B]
    
    # if less than 1 spike persecond
    #len(locs) < 100/(len(sig)/sampling_freq)
    if np.empty(locs):                
        print('No Spike Found!\n')
        return Index, loc
    
    # Threshold for features
    threshold1 = np.mean(sig_TEO)                   

    # for alignment
    locs_s = np.zeros(len(locs))
    # Search Neighborhood window
    S_neighbor = round((wind/2) * sampling_freq)       
                                                                               
    # Initiate original Signal
    # storing templates
    template = np.zeros((len(locs), 2 * S_neighbor))
    # Store METO templates
    S_block = np.zeros((len(locs), 2 * S_neighbor))
    # feature vector
    features = np.zeros((len(locs), 24))
    # window to separate spikes(def was 3.5 ms/ 2ms)
    window = round(0.002 * sampling_freq)

    ## This loop removes the interference in the selected spikes and assigns a label to them
    for i in range(len(locs)):
        ## Case 1      
        if ((locs[i] - S_neighbor) >= 1) and ((locs[i] + S_neighbor) <= len(sig_TEO)):        
            # Find the Neighborhoods
            S_block[i, :] = sig_TEO[(locs[i] - S_neighbor):(locs[i] + S_neighbor)]
            d, _ = sg.find_peaks(abs(sig[(locs[i] - S_neighbor):(locs[i] + S_neighbor)]))
            d_i = min(abs(d - S_neighbor))
            
            if not np.empty(d) and not np.empty(d_i):
                locs_s[i] = locs[i] + (d[d_i] - S_neighbor)
                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]             
            else:
                locs_s[i] = locs[i]
                
            template[i, :] = sig[(locs_s[i] - S_neighbor):(locs_s[i] + S_neighbor)]
            S_block[i, :], template[i, :] = spike_separator(S_block[i, :], template[i, :], S_neighbor, window, threshold)
            features[i, :] = border_detector(S_block[i, :], template[i, :], threshold, threshold1)
            
         ## Case 2
        elif (locs[i] - S_neighbor) < 1:    
            S_block[i, :(locs[i] + S_neighbor)] = sig_TEO[:(locs[i] + S_neighbor)]
            d, _ = sg.find_peaks(abs(sig[:(locs[i] + S_neighbor)]))
            d_i = np.argmin(abs(d - S_neighbor))
           
            if not np.empty(d) and not np.empty(d_i):
                locs_s[i] = locs[i] + (d[d_i] - S_neighbor)
                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]                
            else:
                locs_s[i] = locs[i]
           
            template[i, :(locs_s[i] + S_neighbor)] = sig[:(locs_s[i] + S_neighbor)]
            S_block[i, :], template[i, :] = spike_separator(S_block[i, :], template[i, :], S_neighbor, window, threshold)
            features[i, :] = border_detector(S_block[i, :],template[i, :],threshold,threshold1)
            
        ## Case 3                                  
        # Bounderies
        elif (locs[i] + S_neighbor) > len(sig_TEO):
         
            first_half = len(sig[(locs[i] - S_neighbor):locs[i]])
            complete = len(sig_TEO[(locs[i] - S_neighbor):])
           
            # locate the max in center
            S_block[i, (S_neighbor-first_half):complete] = sig_TEO[(locs[i] - S_neighbor):]
       
            d, _ = sg.find_peaks(abs(sig[(locs[i] - S_neighbor):]))
            d_i = np.argmin(abs(d - S_neighbor))
           
            if not np.empty(d) and not np.empty(d_i):
                locs_s[i] = locs[i] + (d[d_i] - S_neighbor)
                
                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]
                
            else:
                locs_s[i] = locs[i]
            
            first_half = len(sig[(locs_s[i] - S_neighbor):locs_s[i]])
            complete = len(sig_TEO[(locs_s[i] - S_neighbor):])
            template[i, (S_neighbor - first_half):complete] = sig[(locs_s[i] - S_neighbor):]
            S_block[i, :], template[i, :] = spike_separator(S_block[i, :], template[i, :], S_neighbor, window, threshold)                               
            features[i, :] = border_detector(S_block[i, :], template[i, :], threshold, threshold1)                            
  

    Index = locs

    # Mapping features to the range of [1 9]
    map_range = [0, 8]
    original_range = np.zeros(2)
    
    # start from feature 6 which is period of each exterema
    for i in range(5, features.shape[1]):
     
        original_range[0] = min(features[:, i])
        original_range[1] = max(features[:, i])
        if not np.isnan(original_range) and not np.empty(original_range[0]):
            features[:, i] = linear_map(features[:, i], original_range, map_range)
        
    
    # generates the initial set of labels
    title  = generate_titles(features)

    ## Interference cancelation
    #[y,template,Index,title] = inter_cancel(template,Index,title);
    ## make templates
    uniq_c = merge_clusters(template, title, threshold_PsC, sampling_freq, len(sig))
    loc = np.full(template.shape[0], -1)
    
    threshold = threshold_PsC
 
    for i in range(uniq_c.shape[0]):
        tmp, template = find_spikes(uniq_c[i, :], template, locs_s, sampling_freq, threshold)
        # removing too close MUAPs based on their firing pattern
        # to remove too close spikes
        B = (locs_s(tmp))
        B_i = np.argwhere(tmp)
        fire_rate = np.diff(B)
        # 5 milisec separation
        T_rate = fire_rate >= round(0.005*sampling_freq)
        B_F = [B_i[T_rate], B_i[-1]]
        loc[B_F] = i
    
    noise_ind = np.argwhere(loc == -1)
    noise = (loc == -1)
    new_sig = template[noise, :]
    noise = locs_s[noise]
 
    if not np.empty(noise):
        # 5 percent similarity (def was threshold_PsC/2)
        threshold = threshold_PsC
        
        for i in range(uniq_c.shape[0]):
            [tmp,new_sig] = find_spikes(uniq_c[i, :], new_sig, noise, sampling_freq, threshold);
            loc[noise_ind[tmp]] = i;
  
 
        ### Double check the similarity of templates
        #lag
        lag = round(0.008 * sampling_freq)                        
        threshold = 0.50
        for i in range(uniq_c.shape[0]):
            if all(not np.isnan(uniq_c[i, :])):
                for j in range(uniq_c.shape[0]):
                    if (i != j) and (all(not np.isnan(uniq_c[j, :]))):
                        PsC_s = PsC(uniq_c[i, :], uniq_c[j, :], lag)
                        if  PsC_s > threshold:
                            LG = (loc == j)
                            loc[LG] = i
                            
                            if j < max(loc):
                                rg = max(loc) - j;
                                for lk in range(rg):
                                    LG = (loc == (j + lk))
                                    loc[LG] = (j + lk) - 1
                                  
                            uniq_c[j, :] = np.NaN

    #### In case of upsampling its required to downsample everything again
    if upsample_flag > 0: 
        if not np.empty(Index):
            Index = round(Index/upsample_flag);   
        
    return Index, loc
