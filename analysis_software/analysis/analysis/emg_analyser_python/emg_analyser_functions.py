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


def MTEO(raw_signal, ks, FiltFl = True):
    """
    
    Parameters
    ----------
    raw_signal : 1D numpy NDArray[float]
        signal
    ks : 1D numpy NDArray[int]
        levels of MTEO
    FiltFl : boolean
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
        print(tmp[i, :])
        # Filter flag
        if FiltFl:
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
'''
def findspikes(template, sig, locs, Fs, TH):
    """
    Uses Psuedo Correlation for spike Classification
    NOTE: USES PsC_Mex for fast clustering

    Parameters
    ----------
    sig : 1D numpy NDArray[float]
        signal
    DTh : float 
        Decision threshold
    Fs : float
        Sampling frequency
    Returns
    -------
    TE : 1D numpy NDArray[float]
        Detected Muaps 
    """ 
 
    loc = false(1,len(locs));
    lag = round(0.0002*Fs); #lag (def was 0.0002)

      for i = 1:len(locs)
        tmp = sig[i, :];
        [PsC_s,~] = PsC(template,tmp,lag);
        if PsC_s >= TH
             loc(i) = 1;
             sig[i, :] = sig[i, :] - template;
        end
      end
  
      new_sig = sig;
    return loc, new_sig
'''

def resolve_peaks(sig, DTh, Fs):
    """
    Resolves the spikes which are too close

    Parameters
    ----------
    sig : 1D numpy NDArray[int]
        signal
    DTh : float 
        Decision threshold
    Fs : float
        Sampling frequency
        
    Returns
    -------
    TE : 1D numpy NDArray[float]
        Detected Muaps 
    """ 

    sig = np.abs(sig)
    # def 15 millisec min distance
    min_pd = np.round(0.0015 * Fs)
    tmp = np.zeros((1, len(sig)))
    ind = (sig > DTh)
    tmp[ind] = sig[ind]
    locs = sg.find_peaks(tmp, distance = min_pd)
    TE = tmp[locs]
    
    return TE

def MTH(MTEO, ks, L, Fs):
    """
    Multi-Scale Thresholding

    this is the standard energy operator (TEO)
    some people like to invent new names for old concepts and call this "NEO -> nonlinear energy operator"

    Parameters
    ----------
    ks : 1D numpy NDArray[int]
        levels of MTEO
    L : int
        is the factor that multiplies [cost of comission]/[cost of omission].
        For most practical purposes -0.2 <= L <= 0.2. Larger L --> omissions
        likely, smaller L --> false positives likely. For unsupervised
        detection, the suggested value of L is close to 0.
    Fs : float
        Sampling frequency
        
    Returns
    -------
    TE : 1D numpy NDArray[float]
        Detected Muaps
    DTh : float 
        Decision threshold
    """
    
    N, M = MTEO.shape
    ks = ks*2

    # define detection parameter
    # log(Lcom/Lom), where the ratio is the maximum 
    Lmax = -551.0520      
    L = L * Lmax

    for i in range(N):
    
        # take only coefficients that are independent (W(i) apart) for median
        # standard deviation    
        Sigmaj = np.median(np.abs( MTEO[i, ::np.round(ks[i])] - np.mean(MTEO[i, :] )))/0.6745
        #hard threshold
        Thj = Sigmaj * np.sqrt(2 * np.log(M))  
        index = np.abs(MTEO[i, :]) > Thj
        index = MTEO[i, index]
    
        if not np.empty(index):
            # mean of the signal coefficients
            Mj = np.mean(np.abs(index))
            # prior of spikes
            PS = len(index)/M
            # prior of noise
            PN = 1 - PS
            # decision threshold
            DTh = Mj/2 + (Sigmaj**2)/Mj * (L + np.log(PN/PS))
            # make DTh>=0
            DTh = np.abs(DTh) * (DTh >= 0)         
            TE = resolve_peaks(MTEO[i, :], DTh, Fs)
        else:
        
            Mj = Thj;
            # assume at least one spike
            PS = 1/M
            PN = 1 - PS
            # decision threshold
            DTh = Mj/2 + Sigmaj^2/Mj * (L + np.log(PN/PS))
            # make DTh>=0
            DTh = np.abs(DTh)* (DTh >= 0)
            ind  = np.abs(MTEO[i, :]) > DTh
            ind = MTEO(i,ind)
            if np.empty(ind):
                # do nothing ct=[0];
                TE = []
            else:
                # This function resolves too close peaks
                TE = resolve_peaks(MTEO[i, :], DTh, Fs)
                           
    
    # to enhance performance discard detections more than 700Hz period
    if not np.empty(TE):
        if (len(TE)/(np.shape(MTEO)[1]/Fs)) > 500 or (len(TE)/(np.shape(MTEO)[1]/Fs)) < 1:
            TE = []
            DTh = []            
 
    return TE, DTh

def spike_separator(S_block, template, S_neighbor, window, TH):
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
    TH : float
        threshold
         
    Returns
    -------
    S_block : 2D numpy NDArray[float, float]
        Store METO templates
    template : 2D numpy NDArray[float, float]
        Storing templates
    """
 
    # First Part
    Maxima1 = sg.find_peaks(S_block[0, :S_neighbor])
    amp_M1 = S_block[0, Maxima1]
    
    if not np.empty(Maxima1):
        Dist_m = (S_neighbor - (Maxima1 + 1)) >= window
        Dist_a = (amp_M1 >= TH)
          
        if Dist_m and Dist_a:
            #closest to peak
            Maxima1 = Maxima1[0]       
            inverted = 1.01 * max(S_block[0, Maxima1:S_neighbor]) - S_block[0, Maxima1:S_neighbor]
            Minima1 = sg.find_peaks(inverted)
            
            if len(Minima1) > 0:
                Minima1 = Minima1[0]
                Minima1 = Maxima1 + Minima1
                # make the uncorrelated zero
                S_block[0, :Minima1] = 0 
                template[0, :Minima1] = 0
                
        else:
            #do nothing
            S_block[0, :] = S_block[0, :] 
            template[0, :] = template[0, :]
                   
    else:
        S_block[0, :] = S_block[0, :]
        template[0, :] = template[0, :]
         
       
    ## 2nd Part       
    Maxima2 = sg.find_peaks(S_block[0, S_neighbor:])
    amp_M2 = S_block[0, Maxima2]
    
    if not np.empty(Maxima2):
        Dist_m = (Maxima2 + 1 >= window)
        Dist_a = (amp_M2 >= TH)
       
        if Dist_m and Dist_a:
            #closest to peak
            Maxima2 = Maxima2[0]
            
            end_pos = (S_neighbor + Maxima2 + 1)
            if end_pos > S_block.shape(1):
                end_pos = S_block.shape(1)
                
            inverted = 1.01 * max(S_block[0, S_neighbor:end_pos]) - S_block[0, S_neighbor:end_pos]
            
            Minima2 = sg.find_peaks(inverted)
            
            if len(Minima2) > 0:
                Minima2 = Minima2[-1]
                Minima2 = S_neighbor - Minima2
                # make the uncorrelated zero 
                start_pos = (S_block.shape[1] - 1 - Minima2)
                if start_pos < 0:
                    start_pos = 0
                
                #Should be like this? Did as MatLab above.
                #Minima2 = Minima2[-1]
                #Minima2 = Minima2 + S_neighbor
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

def border_detector(S_block, template, TH, TH1):
    """       
    This function Assigns a label to each template  
    
    Parameters
    ----------
    S_block : 2D numpy NDArray[float, float]
        Store METO templates    
    template : 2D numpy NDArray[float, float]
        Storing templates
    TH : float
        threshold
    TH1 : float
        threshold  
        
    Returns
    -------
    features : 1D numpy NDArray[float]
        features of data
       
    """ 
    
    Maxima1 = np.find_peaks(S_block);
    amp_M1 = S_block[Maxima1]
    
    A = amp_M1 > TH
    # Logical Indexing
    B = Maxima1[A]
    
    if len(B) > 5:
        B = B[0:5]
    
    tmp = np.zeros((2*len(B),2));
    D_border = np.zeros((len(B), 1))
    features = np.full(24, np.NaN)
 
    # compute features related to exterema (limited to 3 for now)
    for i in range(len(B)):                   
        # (limited to 5 turns or maximas)
        if i <= 5:  
            dummy = np.argwhere(S_block[:B[i]] <= TH1)
     
            if np.isempty(dummy):
                tmp[i, 0] = np.argwhere(S_block[:B[i]])    
            else:
                tmp[i, 0] = dummy[-1]
                
            tmp[i, 0] = B[i] - tmp[i, 0]
     
            dummy = np.argwhere(S_block[B[i]:] <= TH1)
     
            if np.empty(dummy):
                tmp[i, 1] = np.argmin(S_block[B[i]:])     
            else:
                tmp[i, 1] = dummy[0]
            
            D_border[i, 1] = tmp[i, 0] + tmp[i, 1]

    # See if the peak is a maxima or minima
    #amp = amp_M1(A);
    amp = S_block[B]
    for i in range(len(B)):
        if template(B[i]) < 0:
            # 1 shows a minima
            amp[i] = 1;                               
        else:
            # 2 shows a maxima
            amp[i] = 2;                               
      
    # number of local Max (0 - 4)
    features[0, 0:len(amp)] = amp;       
    # approximate period (5 - 9)
    features[0, 5:(5 + len(D_border))] = D_border
    # time difference between each maxima(10 - 13)
    features[0, 10:(10 + len(np.diff(B)))] = np.diff(B)
    # Amp of Exterma(14 - 18)
    features[0, 14:(14 + len(amp))] = S_block(B)
    # Phase of maximas(19 - 23)
    features[0, 19:(19 + len(amp))] = B  
    # Integral of M_TEO
    #features(1,25) = sum(S_block);
    # RMS of the template                  
    #features(1,26) = rms(S_block);                 

    return features

def initialize(sig, Fs, notch = False):
    """    
    Initialize the signal with filters.
    
    Parameters
    ----------
    Sig : 1D numpy NDArray[float]
        EMG signal Vector
    Fs : float
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

    ## Notch Filter
    if notch:
        # Original MatLab
        # d = designfilt('bandstopiir','FilterOrder',32,
        # 'HalfPowerFrequency1',59,'HalfPowerFrequency2',61, 'DesignMethod','butter','SampleRate',Fs)
        # sig = sg.filtfilt(d, sig)

        # Frequency to be removed from signal (Hz)
        f0 = 60.0
        # Quality factor
        Q = 30.0  
        b_notch, a_notch = sg.iirnotch(f0, Q, fs = Fs)
        
        # Apply notch filter to the noisy signal using signal.filtfilt
        sig = sg.filtfilt(b_notch, a_notch, sig)
    

    ## High-Pass Filter
    # Normalized cutoff frequency
    F_l = 50/(Fs/2)                         
    F_h = 1000/(Fs/2)
    Wn = [F_l, F_h]
    # Butterworth filter
    z, p, k = sg.butter(4, Wn)  
    # Convert to SOS form
    sos = sg.zpk2sos(z, p, k)              
    sig = sg.sosfiltfilt(sos, sig)

    return sig

def TK_filter(sig, Fs, C = 0.1, PsC_TH = 0.1, init = True, wind = 0.020):
    """    
    Function for Spike detection and Classification
    This is designed to filter out shallow peaks out of Action potentials
    with the help of Multi-dimensional TK operator (Teager-Kaiser). The function has several
    subroutins and uses template and label matching in order to cluster the
    action potentials in the signal.
    
    Parameters
    ----------
    Sig : 1D numpy NDArray[float]
        EMG signal Vector
    Fs : float
        Sampling Frequency (e.g. 2000 Hz)
    C : float
        Threshold for the Spike Detection.
        Default 0.6*STD(0.8-1.2)
    PsC_TH : float
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
        sig = initialize(sig, Fs, True)
    
    ## upsampling for better accuracy in Classification

    upsample_flag = 0
    
    if Fs < 10000 and Fs > 4000:
        # upsample by a factor of 5
        sig = sg.resample_poly(sig, 5, 1)  
        Fs = 5 * Fs
        upsample_flag = 5
    elif Fs > 10000 and Fs < 15000:
        # upsample by a factor of 2 
        sig = sg.resample_poly(sig, 2, 1)
        Fs = 2 * Fs
        upsample_flag = 2
    elif Fs <= 3000:
        sig = sg.resample_poly(sig, 8, 1)
        Fs = 8 * Fs
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
    locs, TH = MTH(sig_TEO, ks, C, Fs)

    # Removing those peaks on begining and end of sig
    # Minus 1, as Python indexes start at 0
    A = locs > round((wind)*Fs) - 1
    locs = locs[A]
    B = locs < (len(sig) - round((wind)*Fs) - 1)
    locs = locs[B]
    
    # if less than 1 spike persecond
    #len(locs) < 100/(len(sig)/Fs)
    if np.empty(locs):                
        print('No Spike Found!\n')
        return Index, loc
    
    # Threshold for features
    TH1 = np.mean(sig_TEO)                   

    # for alignment
    locs_s = np.zeros(len(locs))
    # Search Neighborhood window
    S_neighbor = round((wind/2) * Fs)       
                                                                               
    # Initiate original Signal
    # storing templates
    template = np.zeros((len(locs), 2 * S_neighbor))
    # Store METO templates
    S_block = np.zeros((len(locs), 2 * S_neighbor))
    # feature vector
    features = np.zeros((len(locs), 24))
    # window to separate spikes(def was 3.5 ms/ 2ms)
    window = round(0.002 * Fs)

    ## This loop removes the interference in the selected spikes and assigns a label to them
    for i in range(len(locs)):
        ## Case 1      
        if ((locs[i] - S_neighbor) >= 1) and ((locs[i] + S_neighbor) <= len(sig_TEO)):        
            # Find the Neighborhoods
            S_block[i, :] = sig_TEO[(locs[i] - S_neighbor):(locs[i] + S_neighbor)]
            d = sg.find_peaks(abs(sig[(locs[i] - S_neighbor):(locs[i] + S_neighbor)]))
            d_i = min(abs(d - S_neighbor))
            
            if not np.empty(d) and not np.empty(d_i):
                locs_s[i] = locs[i] + (d[d_i] - S_neighbor)
                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]             
            else:
                locs_s[i] = locs[i]
                
            template[i, :] = sig[(locs_s[i] - S_neighbor):(locs_s[i] + S_neighbor)]
            S_block[i, :], template[i, :] = spike_separator(S_block[i, :], template[i, :], S_neighbor, window, TH)
            features[i, :] = border_detector(S_block[i, :], template[i, :], TH, TH1)
            
         ## Case 2
        elif (locs[i] - S_neighbor) < 1:    
            S_block[i, :(locs[i] + S_neighbor)] = sig_TEO[:(locs[i] + S_neighbor)]
            d = sg.find_peaks(abs(sig[:(locs[i] + S_neighbor)]))
            d_i = np.argmin(abs(d - S_neighbor))
           
            if not np.empty(d) and not np.empty(d_i):
                locs_s[i] = locs[i] + (d[d_i] - S_neighbor)
                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]                
            else:
                locs_s[i] = locs[i]
           
            template[i, :(locs_s[i] + S_neighbor)] = sig[:(locs_s[i] + S_neighbor)]
            S_block[i, :], template[i, :] = spike_separator(S_block[i, :], template[i, :], S_neighbor, window, TH)
            features[i, :] = border_detector(S_block[i, :],template[i, :],TH,TH1)
            
         ## Case 3                                  
         # Bounderies
        elif (locs[i] + S_neighbor) > len(sig_TEO):
         
            first_half = len(sig[(locs[i] - S_neighbor):locs[i]])
            complete = len(sig_TEO[(locs[i] - S_neighbor):])
           
            # locate the max in center
            S_block[i, (S_neighbor-first_half):complete] = sig_TEO[(locs[i] - S_neighbor):]
       
            d = sg.find_peaks(abs(sig[(locs[i] - S_neighbor):]))
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
            S_block[i, :], template[i, :] = spike_separator(S_block[i, :], template[i, :], S_neighbor, window, TH)                               
            features[i, :] = border_detector(S_block[i, :], template[i, :], TH, TH1)                            
  

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
    title  = generate_title(features)

    ## Interference cancelation
    #[y,template,Index,title] = inter_cancel(template,Index,title);
    ## make templates
    uniq_c = merge_clusters(template, title, PsC_TH, Fs, len(sig))
    loc = np.full(template.shape[0], -1)
    
    TH = PsC_TH
 
    for i in range(uniq_c.shape[0]):
        tmp, template = find_spikes(uniq_c[i, :], template, locs_s, Fs, TH)
        # removing too close MUAPs based on their firing pattern
        # to remove too close spikes
        B = (locs_s(tmp))
        B_i = np.argwhere(tmp)
        fire_rate = np.diff(B)
        # 5 milisec separation
        T_rate = fire_rate >= round(0.005*Fs)
        B_F = [B_i[T_rate], B_i[-1]]
        loc[B_F] = i
    
    noise_ind = np.argwhere(loc == -1)
    noise = (loc == -1)
    new_sig = template[noise, :]
    noise = locs_s[noise]
 
    if not np.empty(noise):
        # 5 percent similarity (def was PsC_TH/2)
        TH = PsC_TH
        
        for i in range(uniq_c.shape[0]):
            [tmp,new_sig] = find_spikes(uniq_c[i, :], new_sig, noise, Fs, TH);
            loc[noise_ind[tmp]] = i;
  
 
        ### Double check the similarity of templates
        #lag
        lag = round(0.008 * Fs)                        
        TH = 0.50
        for i in range(uniq_c.shape[0]):
            if all(not np.isnan(uniq_c[i, :])):
                for j in range(uniq_c.shape[0]):
                    if (i != j) and (all(not np.isnan(uniq_c[j, :]))):
                        PsC_s = PsC(uniq_c[i, :], uniq_c[j, :], lag)
                        if  PsC_s > TH:
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
