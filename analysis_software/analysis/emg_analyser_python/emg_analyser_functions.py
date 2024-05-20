#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
These functions are reimplemented in Python by Richard Howey
2024, RSE team, Newcastle University
The comments are mostly taken from original code.
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

import numpy as np
import scipy.signal as sg
from emg_analyser_python.detect_peaks import detect_peaks
from emg_analyser_python.constants import QUICK_VERSION

MAP_RANGE = [1, 9]


def round_int(val):
    """
    Rounds the given float to the nearest integer.

    Parameters
    ----------
    val : float
        number to be rounded

    Returns
    -------
    integer

    """

    return round_int_banker(val)
    # return int(np.round(val))


def round_ints(vals):
    """
    Rounds the given array of floats to the nearest integers.

    Parameters
    ----------
    val : 1D numpy NDArray[float]
        number to be rounded

    Returns
    -------
    1D numpy NDArray[int]

    """

    return round_ints_banker(vals)
    # return np.round(vals)


def round_int_banker(val):
    """
    Rounds the given float to the nearest integer.
    In the case of a value half way the number
    is rounded up to be consistent with MatLab, e.g. 0.5 rounds to 1.

    Parameters
    ----------
    val : float
        number to be rounded

    Returns
    -------
    integer

    """

    if np.isnan(val):
        return val

    # Avoid rounding down when half way. If first decimal is 5
    # then add a bit to ensure it rounds up
    first_dec = int((val % 1) * 10)

    if first_dec == 5:
        if val > 0:
            val += 0.1
        else:
            val -= 0.1

    return int(np.round(val))


def round_ints_banker(vals):
    """
    Rounds the given array of floats to the nearest integers.
    In the case of a values half way the numbers
    are rounded up to be consistent with MatLab, e.g. 0.5 rounds to 1.

    Parameters
    ----------
    val : 1D numpy NDArray[float]
        number to be rounded

    Returns
    -------
    1D numpy NDArray[int]

    """

    return np.array([round_int(x) for x in vals])


def find_peaks(data, distance=1):
    """
    Try to return as near as possible the same answer as findpeaks in MatLab
    """

    if QUICK_VERSION:
        peaks, _ = sg.find_peaks(data, distance=distance)
        return peaks
    else:
        return detect_peaks(data, mpd=distance)


def running_TEO(raw_signal, k=1):
    """
    calcs the function x(n)^2 - x(n-k)*x(n+k)

    this is the standard energy operator (TEO)
    some people like to invent new names for old concepts
    and call this "NEO -> nonlinear energy operator"

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


def multi_teager_energy_operator(raw_signal, ks, filter=True):
    """
    Teager Energy Operator (TEO) mainly shows the frequency and instantaneous
    changes of the signal amplitude that is very sensitive to subtle changes.

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
            # ensure the sample variance is used and not the population variance
            # by setting ddof = 1
            v[i] = np.var(tmp[i, :], ddof=1)

            # apply the window
            win = np.hamming(4 * ks[i] + 1)

            tmp[i, :] = sg.filtfilt(win, 1, tmp[i, :]) / (v[i])  # def was v unsquared

    if L > 1:
        runTEO = np.sum(tmp, axis=0)
    else:
        runTEO = tmp[i, :]

    return runTEO, tmp


def psuedo_correlation(template, sig, lag=None):
    """
    Psuedo_Correlation
    Computes the Pseudo Correlation, a finer approach than normal
    correlation for template matching. Please review the paper below in order
    to see why it is much more accurate for the pattern recognition

    Only does (-lag, lag]. i.e. not including -lag as defined in MatLab code.
    Increase max_lag by 1 to include -lag

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
    psuedo_correlation_score : float
        maximum score at best lag
    best_lag : int
        best lag
    """

    if lag is None:
        lag = round_int(len(sig) * 0.5)

    m = len(template)
    n = len(sig)

    if m != n:
        raise Exception("Length of Template should be equal to pattern")

    sig = np.hstack((np.zeros((lag)), sig, np.zeros((2 * lag))))

    # If the lag is too great then extreme lags always result in zero
    # so no need to calculate for some lags
    min_lag = 0
    if m < lag:
        min_lag = lag - m

    max_lag = 2 * lag + 1
    if max_lag > n + lag + 1:
        max_lag = n + lag + 1

    # Define matrices so that all the calculations
    # can be done at once to speed things up
    no_rows = max_lag - min_lag

    template_mat = np.full((no_rows, m), template)
    shifted_sig = np.zeros((no_rows, m))

    for k in range(min_lag, max_lag):
        shifted_sig[k - min_lag, :] = sig[k : (k + m)]

    # calculate the "pseudo correlation" for each shifted signal and then take the max
    p1 = template_mat * shifted_sig
    p2 = np.fabs(template_mat - shifted_sig)
    p3 = np.maximum(np.fabs(template_mat), np.fabs(shifted_sig))

    p4 = p1 - p2 * p3
    sum_p4 = np.sum(p4, axis=1)

    positive_sum_p4 = sum_p4[sum_p4 > 0]

    # Take the maximum from the positive results if there are any,
    # otherwise the pseudo correlation is zero
    if positive_sum_p4.size:
        p3 = p3[sum_p4 > 0]
        psuedo_correlation_score = np.max(positive_sum_p4 / np.sum(p3 * p3, axis=1))
    else:
        psuedo_correlation_score = 0

    return psuedo_correlation_score


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
    spike_locs : 1D numpy NDArray[int]
        location of the spikes in the signal
    new_sigs : 2D numpy NDArray[float, float]
        new signal

    """

    spike_locs = np.full(len(locs), False)

    # lag (def was 0.0002)
    lag = round_int(0.0002 * sampling_freq)

    for i in range(len(locs)):

        psuedo_correlation_score = psuedo_correlation(templates, sigs[i, :], lag)

        if psuedo_correlation_score >= threshold:
            spike_locs[i] = True
            sigs[i, :] = sigs[i, :] - templates

    return spike_locs, sigs


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
    val = 0.0015 * sampling_freq
    min_pd = int(np.max((1, round_int(val))))

    tmp = np.zeros(len(sig))
    ind = sig > decision_thres
    tmp[ind] = sig[ind]

    TE = find_peaks(tmp, distance=min_pd)

    return TE


def multi_scale_thresholding(MTEO, ks, L, sampling_freq):
    """
    Multi-Scale Thresholding

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

    # Ensure consistent dimensions if a vector is given
    if MTEO.ndim < 2:
        MTEO = MTEO.reshape(1, -1)

    N, M = MTEO.shape

    ks = ks * 2

    # define detection parameter
    # log(Lcom/Lom), where the ratio is the maximum
    Lmax = -551.0520
    L = L * Lmax

    for i in range(N):
        # take only coefficients that are independent (W(i) apart) for median
        # standard deviation
        Sigmaj = np.median(np.abs(MTEO[:: round_int(ks[i])] - np.mean(MTEO))) / 0.6745
        # hard threshold
        Thj = Sigmaj * np.sqrt(2 * np.log(M))
        indexes = np.abs(MTEO[i, :]) > Thj

        if len(indexes) > 0:
            sig_out = MTEO[i, indexes]
            # mean of the signal coefficients
            Mj = np.mean(np.abs(sig_out))
            # prior of spikes
            PS = len(sig_out) / M
            # prior of noise
            PN = 1 - PS
            # decision threshold
            decision_thres = Mj / 2 + (Sigmaj**2) / Mj * (L + np.log(PN / PS))
            # make decision_thres>=0
            decision_thres = np.abs(decision_thres) * (decision_thres >= 0)
            TE = resolve_peaks(MTEO[i, :], decision_thres, sampling_freq)
        else:

            Mj = Thj
            # assume at least one spike
            PS = 1 / M
            PN = 1 - PS
            # decision threshold
            decision_thres = Mj / 2 + Sigmaj ^ 2 / Mj * (L + np.log(PN / PS))
            # make decision_thres>=0
            decision_thres = np.abs(decision_thres) * (decision_thres >= 0)
            ind = np.abs(MTEO[i, :]) > decision_thres
            ind = MTEO[i, ind]
            if not ind.size:
                # do nothing ct=[0]
                TE = []
            else:
                # This function resolves too close peaks
                TE = resolve_peaks(MTEO[i, :], decision_thres, sampling_freq)

    # to enhance performance discard detections more than 700Hz period
    if len(TE) > 0:
        herz = TE.shape[0] / (MTEO.shape[1] / sampling_freq)
        if herz > 500 or herz < 1:
            TE = []
            decision_thres = []

    return np.array(TE), decision_thres


def spike_separator(S_block, template, S_neighbor, window, threshold):
    """
    Divides the Spike in two sections
    Removes the second pulse superimposed if it is far enough from another
    Spike

    Parameters
    ----------
    S_block : 1D numpy NDArray[float]
        Store METO templates
    template : 1D numpy NDArray[float]
        Storing templates
    S_neighbor : integer
        Search Neighborhood window size
    window : integer
        Window to separate spikes
    threshold : float
        threshold

    Returns
    -------
    S_block : 1D numpy NDArray[float]
        Store METO templates
    template : 1D numpy NDArray[float]
        Storing templates
    """

    # First Part
    maxima_1 = find_peaks(S_block[:S_neighbor])

    if len(maxima_1) > 0:
        amp_M1 = S_block[:S_neighbor][maxima_1]
        dist_m = (S_neighbor - (maxima_1 + 1)) >= window
        dist_a = amp_M1 >= threshold
        maxima_1 = maxima_1[dist_m & dist_a]

        if len(maxima_1) > 0:
            # closest to peak
            maxima_1 = maxima_1[0]
            inverted = (
                1.01 * np.max((S_block[maxima_1:S_neighbor]))
                - S_block[maxima_1:S_neighbor]
            )
            minima_1 = find_peaks(inverted)

            if len(minima_1) > 0:
                minima_1 = minima_1[0]
                end_pos = maxima_1 + minima_1 + 2
                # make the uncorrelated zero
                S_block[:end_pos] = 0
                template[:end_pos] = 0

    # 2nd Part
    maxima_2 = find_peaks(S_block[(S_neighbor - 1) :])

    if len(maxima_2) > 0:
        amp_M2 = S_block[(S_neighbor - 1) :][maxima_2]
        dist_m = maxima_2 + 1 >= window
        dist_a = amp_M2 >= threshold
        maxima_2 = maxima_2[dist_m & dist_a]

        if len(maxima_2) > 0:
            # closest to peak
            maxima_2 = maxima_2[0]

            end_pos = S_neighbor - 1 + maxima_2 + 1
            if end_pos > len(S_block):
                end_pos = len(S_block)

            inverted = (
                1.01 * np.max(S_block[(S_neighbor - 1) : end_pos])
                - S_block[(S_neighbor - 1) : end_pos]
            )

            minima_2 = find_peaks(inverted)

            if len(minima_2) > 0:
                minima_2 = minima_2[-1]
                minima_2 = S_neighbor - 1 - minima_2

                # make the uncorrelated zero
                start_pos = len(S_block) - 1 - minima_2
                if start_pos < 0:
                    start_pos = 0

                S_block[start_pos:] = 0
                template[start_pos:] = 0

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

    maxima_1 = find_peaks(S_block)
    amp_M1 = S_block[maxima_1]

    A = amp_M1 > threshold
    # Logical Indexing
    B = maxima_1[A]

    if len(B) > 5:
        B = B[0:5]

    tmp = np.zeros((2 * len(B), 2))
    D_border = np.zeros(len(B))
    features = np.full(24, np.NaN)

    # compute features related to exterema (limited to 3 for now)
    for i in range(len(B)):
        # (limited to 5 turns or maximas)
        if i < 5:
            dummy = np.argwhere(S_block[: (B[i] + 1)] <= threshold1)

            if len(dummy) == 0:
                tmp[i, 0] = np.nanargmin(S_block[: (B[i] + 1)])
            else:
                tmp[i, 0] = dummy[-1]

            tmp[i, 0] = B[i] - tmp[i, 0]

            dummy = np.argwhere(S_block[B[i] :] <= threshold1)

            if len(dummy) == 0:
                tmp[i, 1] = np.nanargmin(S_block[B[i] :])
            else:
                tmp[i, 1] = dummy[0]

            D_border[i] = tmp[i, 0] + tmp[i, 1]

    # See if the peak is a maxima or minima
    amp = S_block[B]
    for i in range(len(B)):
        if template[B[i]] < 0:
            # 1 shows a minima
            amp[i] = 1
        else:
            # 2 shows a maxima
            amp[i] = 2

    # number of local Max (0 - 4)
    features[0 : len(amp)] = amp
    # approximate period (5 - 9)
    features[5 : (5 + len(D_border))] = D_border + 1
    # time difference between each maxima(10 - 13)
    features[10 : (10 + len(np.diff(B)))] = np.diff(B)
    # Amp of Exterma(14 - 18)
    features[14 : (14 + len(amp))] = S_block[B]
    # Phase of maximas(19 - 23)
    features[19 : (19 + len(amp))] = B + 1
    # Integral of M_TEO
    # features(1,25) = sum(S_block)
    # RMS of the template
    # features(1,26) = rms(S_block)

    return features


def initialize(sig, sampling_freq):
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

    # Initialzie
    # Remove the baseline shift
    sig = sg.detrend(sig)
    # Remove mean
    sig = sig - np.mean(sig)
    # Normalize st. deviation
    sig = sig / np.std(sig, ddof=1)

    # Band-Pass Filter
    # Normalized cutoff frequency
    F_l = 50 / (sampling_freq / 2)
    F_h = 1000 / (sampling_freq / 2)
    Wn = [F_l, F_h]
    # Butterworth filter
    sos = sg.butter(4, Wn, btype="bandpass", output="sos")
    sig = sg.sosfiltfilt(sos, sig)

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
    Y : 1D numpy NDArray[int]
        Mapped number
    """

    a1 = original_range[0]
    a2 = original_range[1]

    b1 = map_range[0]
    b2 = map_range[1]

    if original_range[0] != original_range[1]:
        Y = b1 + ((np.asarray(X) - a1) * (b2 - b1)) / (a2 - a1)
    else:
        Y = np.asarray(X) / original_range[0]

    # map to nearest integers
    return round_ints(Y)


def linear_map2(X, original_range, map_range1, map_range2):
    """
    Linearly Maps a set of numbers to another scale

    Parameters
    ----------
    X : 1D numpy NDArray[float]
        The number to be mapped
    original_range : 1D numpy NDArray[float]
        The original range of the variable e.g. ([0 10]), the
        minimum and maximum possible value that X can take
    map_range1 : 1D numpy NDArray[float]
        The new min and maximum range that the numbers in the
        first 5 and last 5 should be assigned to that range
    map_range2 : 1D numpy NDArray[float]
        The new min and maximum range that the numbers should be
        assigned to that range

    Returns
    -------
    Y : 1D numpy NDArray[int]
        Mapped number
    """

    a1 = original_range[0]
    a2 = original_range[1]

    b1 = map_range1[0]
    b2 = map_range1[1]

    # map first and last 5 with range1
    Y1 = b1 + ((np.asarray(X)[:5] - a1) * (b2 - b1)) / (a2 - a1)
    Y3 = b1 + ((np.asarray(X)[-5:] - a1) * (b2 - b1)) / (a2 - a1)

    b1 = map_range2[0]
    b2 = map_range2[1]

    # map middle elements with range2
    Y2 = b1 + ((np.asarray(X)[5:-5] - a1) * (b2 - b1)) / (a2 - a1)

    Y = np.hstack((Y1, Y2, Y3))

    return round_ints(Y)


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
        Considered the same if first 5 numbers are the same
        and the other numbers are the same or differ by exactly 1
    """

    no_features = features.shape[0]

    if no_features == 0:
        return []

    # Replace NaNs with this number, other numbers should be below
    # this number so will not conflict
    # We need NaNs to be considered equal when comparing features
    features[np.isnan(features)] = MAP_RANGE[1] + 1

    # Label first list of features as "1"
    titles = np.zeros(no_features)
    title_counter = 0

    # First 5 and last 5 elements must be equal.
    # Create groups where these are equal firstly
    _, uni_indices, uni_inv_ind = np.unique(
        np.hstack((features[:, :5], features[:, -5:])),
        return_index=True,
        return_inverse=True,
        axis=0,
    )

    # Loop through unique sets
    for idx_count, idx in enumerate(uni_indices):
        in_set = (np.argwhere(idx_count == uni_inv_ind)).flatten()  # orig indx

        # Current list of feature groups to check if a list of features belongs to it
        features_to_check = np.full(len(in_set), -1)
        features_to_check[0] = in_set[0]
        features_to_check_count = 1
        title_counter += 1
        titles[idx] = title_counter

        for i in in_set[1:]:

            for k in range(features_to_check_count):
                j = features_to_check[k]

                # Check if remaining elements are the same or differ by exactly 1
                diff = np.abs(features[j, 5:-5] - features[i, 5:-5])

                if ((diff == 0) | (diff == 1)).all():
                    # Considered the same, so give the same title
                    titles[i] = titles[j]
                    break

            # Does not match any previous feature groups so give a new "title"
            if titles[i] == 0:
                title_counter += 1
                titles[i] = title_counter
                features_to_check[features_to_check_count] = i
                features_to_check_count += 1

    return titles


def generate_titles2(features):
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
        Considered the same if first 5 numbers are the same
        and the other numbers are the same or differ by exactly 1
    """

    no_features = features.shape[0]

    if no_features == 0:
        return []

    # Replace NaNs with this number, other numbers should be below
    # this number so will not conflict
    # We need NaNs to be considered equal when comparing features
    features[np.isnan(features)] = MAP_RANGE[1] + 1

    # All elements must be equal. Create groups where these are equal firstly
    _, uni_inv_ind = np.unique(features, return_inverse=True, axis=0)

    return uni_inv_ind + 1


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

    no_unique_titles = int(np.max(titles))
    c = 0
    semi_final = np.zeros((no_unique_titles, template.shape[1]))
    counter = np.full(no_unique_titles, False)

    if round_int(sig_len / sampling_freq) < 10:
        # minimum length of clusters
        min_l = np.ceil(sig_len / sampling_freq)
    else:
        min_l = 3

    # lag(def 0.0002)
    lag = round_int(0.0002 * sampling_freq)

    # Checking for inter-cluster similarity
    for tit in range(1, no_unique_titles + 1):
        A = titles == tit
        tmp_t2 = template[A, :]

        if tmp_t2.shape[0] >= min_l:
            semi_final[c, :] = np.median(tmp_t2, axis=0)

            for j in range(tmp_t2.shape[0]):
                psuedo_correlation_score = psuedo_correlation(
                    semi_final[c, :], tmp_t2[j, :], 4
                )

                if psuedo_correlation_score < threshold:
                    tmp_t2[j, :] = np.NaN

            tmp_t2 = tmp_t2[np.isfinite(tmp_t2[:, 0]), :]

            if tmp_t2.shape[0] < min_l:
                semi_final[c, :] = np.NaN
                counter[c] = False
            else:
                semi_final[c, :] = np.median(tmp_t2, axis=0)
                counter[c] = True

            c = c + 1

    # Now merging clusters that are similar
    semi_final = semi_final[counter, :]

    for i in range(semi_final.shape[0]):
        if not np.isnan(semi_final[i, :]).any():
            for j in range(semi_final.shape[0]):  # range(i):
                if i != j and not np.isnan(semi_final[j, :]).any():
                    psuedo_correlation_score = psuedo_correlation(
                        semi_final[i, :], semi_final[j, :], lag
                    )
                    if psuedo_correlation_score > threshold:
                        semi_final[i, :] = (semi_final[i, :] + semi_final[j, :]) * 0.5
                        semi_final[j, :] = np.NaN

    uniq_c = semi_final[np.isfinite(semi_final[:, 0]), :]

    return uniq_c


def TK_filter(sig, sampling_freq, C=0.1, threshold_PsC=0.1, init=True, wind=0.004):
    """
    Function for Spike detection and Classification
    This is designed to filter out shallow peaks out of Action potentials
    with the help of Multi-dimensional TK operator (Teager-Kaiser).
    The function has several subroutines and uses template and label matching
    in order to cluster the action potentials in the signal.

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
    Index : 1D numpy NDArray[int]
        Index of MUAPs clustered
    loc : 1D numpy NDArray[int]
        location of the MUAPs in the signal
    """

    # Initialzie and highpass filter
    # Detrends and band-pass filters the signal
    if init:
        sig = initialize(sig, sampling_freq)

    # upsampling for better accuracy in Classification

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

    # MTEO
    # Scales for MTEO (or 1,3,5) detection
    ks = np.array([2, 3, 5])
    if upsample_flag > 0:
        ks = ks * 2

    # First Stage Spike detection
    # Compute MTEO
    sig_TEO, _ = multi_teager_energy_operator(sig, ks)
    locs, threshold = multi_scale_thresholding(sig_TEO, ks, C, sampling_freq)

    # Removing those peaks on begining and end of sig
    # Minus 1, as Python indexes start at 0
    A = locs > round_int((wind) * sampling_freq) - 1
    locs = locs[A]
    B = locs < (len(sig) - round_int((wind) * sampling_freq) - 1)
    locs = locs[B]

    # if less than 1 spike persecond
    # len(locs) < 100/(len(sig)/sampling_freq)
    if not locs.size:
        return Index, loc

    # Threshold for features
    threshold1 = np.mean(sig_TEO)

    # for alignment
    locs_s = np.zeros(len(locs))
    # Search Neighborhood window
    S_neighbor = round_int((wind / 2) * sampling_freq)

    # Initiate original Signal
    # storing templates
    template = np.zeros((len(locs), 2 * S_neighbor))
    # Store METO templates
    S_block = np.zeros((len(locs), 2 * S_neighbor))
    # feature vector
    features = np.zeros((len(locs), 24))
    # window to separate spikes(def was 3.5 ms/ 2ms)
    window = round_int(0.002 * sampling_freq)

    # This loop removes the interference in the selected spikes
    # and assigns a label to them
    for i in range(len(locs)):

        # Case 1
        if ((locs[i] - S_neighbor) >= 0) and ((locs[i] + S_neighbor) < len(sig_TEO)):
            # Find the Neighborhoods
            S_block[i, :] = sig_TEO[
                (locs[i] - S_neighbor + 1) : (locs[i] + S_neighbor + 1)
            ]
            d = find_peaks(
                np.abs(sig[(locs[i] - S_neighbor + 1) : (locs[i] + S_neighbor + 1)])
            )

            if d.size:
                d_i = np.nanargmin(np.abs(d + 1 - S_neighbor))
                locs_s[i] = locs[i] + (d[d_i] + 1 - S_neighbor)

                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]
            else:
                locs_s[i] = locs[i]

            template[i, :] = sig[
                (int(locs_s[i]) - S_neighbor + 1) : (int(locs_s[i]) + S_neighbor + 1)
            ]
            S_block[i, :], template[i, :] = spike_separator(
                S_block[i, :], template[i, :], S_neighbor, window, threshold
            )
            features[i, :] = border_detector(
                S_block[i, :], template[i, :], threshold, threshold1
            )

        # Case 2
        elif (locs[i] - S_neighbor) < 0:
            end_loc = int(locs[i]) + S_neighbor + 1
            S_block[i, :end_loc] = sig_TEO[:end_loc]
            d = find_peaks(np.fabs(sig[:end_loc]))
            d_i = np.nanargmin(np.fabs(d + 1 - S_neighbor))

            if d.size and d_i.size:
                locs_s[i] = locs[i] + (d[d_i] + 1 - S_neighbor)
                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]
            else:
                locs_s[i] = locs[i]

            s_end_loc = int(locs_s[i]) + S_neighbor
            template[i, :s_end_loc] = sig[:s_end_loc]
            S_block[i, :], template[i, :] = spike_separator(
                S_block[i, :], template[i, :], S_neighbor, window, threshold
            )
            features[i, :] = border_detector(
                S_block[i, :], template[i, :], threshold, threshold1
            )

        # Case 3
        # Bounderies
        elif (locs[i] + S_neighbor) >= len(sig_TEO):
            first_half = len(sig[(locs[i] - S_neighbor) : locs[i]])
            complete = len(sig_TEO[(locs[i] - S_neighbor) :])

            # locate the max in center
            S_block[i, (S_neighbor - first_half) : complete] = sig_TEO[
                (locs[i] - S_neighbor) :
            ]

            d = find_peaks(np.fabs(sig[(locs[i] - S_neighbor) :]))
            d_i = np.nanargmin(np.abs(d + 1 - S_neighbor))

            if d.size and d_i.size:
                locs_s[i] = locs[i] + (d[d_i] + 1 - S_neighbor)

                if locs_s[i] < S_neighbor:
                    locs_s[i] = locs[i]

            else:
                locs_s[i] = locs[i]

            first_half = len(sig[(locs_s[i] - S_neighbor + 1) : locs_s[i]])
            complete = len(sig_TEO[(locs_s[i] - S_neighbor + 1) :])
            template[i, (S_neighbor - first_half + 1) : complete] = sig[
                (locs_s[i] - S_neighbor) :
            ]
            S_block[i, :], template[i, :] = spike_separator(
                S_block[i, :], template[i, :], S_neighbor, window, threshold
            )
            features[i, :] = border_detector(
                S_block[i, :], template[i, :], threshold, threshold1
            )

    Index = locs

    # Mapping features to the range of [1 9]
    original_range = np.zeros(2)

    # start from feature 6 which is period of each exterema
    for i in range(5, features.shape[1]):

        original_range[0] = np.nanmin(features[:, i])
        original_range[1] = np.nanmax(features[:, i])
        if QUICK_VERSION:
            features[:, i] = linear_map2(
                features[:, i], original_range, MAP_RANGE, [1, 4]
            )  # idea for speed up for clustering, change below also.
            # Does work a bit, but more MUs
        else:
            features[:, i] = linear_map(features[:, i], original_range, MAP_RANGE)

    if QUICK_VERSION:
        titles = generate_titles2(features)
    else:
        titles = generate_titles(features)

    uniq_c = merge_clusters(template, titles, threshold_PsC, sampling_freq, len(sig))

    loc = np.full(template.shape[0], -1)

    threshold = threshold_PsC

    for i in range(uniq_c.shape[0]):
        tmp, template = find_spikes(
            uniq_c[i, :], template, locs_s, sampling_freq, threshold
        )
        # removing too close MUAPs based on their firing pattern
        # to remove too close spikes
        B = locs_s[tmp]
        B_i = np.argwhere(tmp)
        fire_rate = np.diff(B)

        # 5 milisec separation
        T_rate = fire_rate >= round_int(0.005 * sampling_freq)
        T_rate = np.concatenate((T_rate, np.array([True])))

        B_F = B_i[T_rate]
        loc[B_F] = i

    noise_ind = np.argwhere(loc == -1)
    noise = loc == -1
    new_sig = template[noise, :]
    noise = locs_s[noise]

    if noise.size:
        # 5 percent similarity (def was threshold_PsC/2)
        threshold = threshold_PsC

        for i in range(uniq_c.shape[0]):
            tmp, new_sig = find_spikes(
                uniq_c[i, :], new_sig, noise, sampling_freq, threshold
            )
            loc[noise_ind[tmp]] = i

    # Double check the similarity of templates
    # lag
    lag = round_int(0.008 * sampling_freq)
    threshold = 0.50
    for i in range(uniq_c.shape[0]):
        if not np.isnan(uniq_c[i, :]).any():
            for j in range(uniq_c.shape[0]):
                if i != j and not np.isnan(uniq_c[j, :]).any():
                    psuedo_correlation_score = psuedo_correlation(
                        uniq_c[i, :], uniq_c[j, :], lag
                    )

                    if psuedo_correlation_score > threshold:
                        # i and j similar so give the same value
                        loc[loc == j] = i

                        # take one away from loc labels higher than j,
                        # as j has been removed (relabelled as i)
                        if j < np.max(loc):
                            for ch in range(j + 1, np.max(loc) + 1):
                                loc[loc == ch] = ch - 1

                        uniq_c[j, :] = np.NaN

    # In case of upsampling its required to downsample everything again
    if upsample_flag > 0:
        if Index.size:
            Index = round_ints(Index / upsample_flag)

    return Index, loc
