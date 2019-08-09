"""
Copyright 2019 Dominik Werner

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from matplotlib.mlab import specgram
import numpy as np


def spectrogram(signal, window_length, n_overlap, fs=1, f_max=None, f_min=None,
                outlier_threshold_low=None, outlier_threshold_high=None):
    """
    Calculates the spectrogram of the given time trace. (Uses mlab implementation)
    :param signal: time trace
    :param window_length: number of samples per FFT spectrum (should be a power of two)
    :param n_overlap: the number of overlapping samples with neighbouring windows
    :param fs: the sampling frequency (1 Hz by default)
    :param f_max: Maximum frequency present in the output (whole spectrum if not specified)
    :param f_min: Minimum frequency present in the output (whole spectrum if not specified)
    :param outlier_threshold_low: All values which are less than this value below the mean will be smoothed
    :param outlier_threshold_high: All values which are more than this value above the mean will be smoothed
    :return: array of spectra over time, frequencies, time
    """
    de_trend = None                        # do not try to remove trends from the data
    sides = 'onesided'                     # only return positive frequencies (would also be the case for "default" and "psd")
    window = np.hamming(window_length)     # use hamming window
    pad_to = window_length                 # to number of points to which the data segment is padded during the FFT
    scale_by_freq = True                   # gives the result in dB/Hz
    mode = 'psd'                           # use the PSD for the spectra

    spec, f, t = specgram(x=signal, NFFT=window_length, Fs=fs,
                          detrend=de_trend, window=window,
                          noverlap=n_overlap, pad_to=pad_to,
                          sides=sides,
                          scale_by_freq=scale_by_freq,
                          mode=mode)

    # crop data to defined frequency range
    if f_max is not None:
        idx_max = f <= f_max
        spec = spec[idx_max, :]
        f = f[idx_max]
    if f_min is not None:
        idx_min = f >= f_min
        spec = spec[idx_min, :]
        f = f[idx_min]

    # convert data to dB scale
    spec_dB = 10. * np.log10(spec)
    spec_mean = np.mean(spec_dB)

    # smooth outlier frames
    if outlier_threshold_low is not None:
        spec_lower_limit = spec_mean - outlier_threshold_low
        spec_dB[spec_dB < spec_lower_limit] = spec_lower_limit
    if outlier_threshold_high is not None:
        spec_upper_limit = spec_mean + outlier_threshold_high
        spec_dB[spec_dB > spec_upper_limit] = spec_upper_limit

    return spec_dB, f, t