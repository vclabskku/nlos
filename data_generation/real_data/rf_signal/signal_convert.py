import numpy as np
import math


def _resizing(x_t, y_t):
    x_size = x_t.size
    y_size = y_t.size
    if x_size > y_size:
        z_x = np.zeros(x_size * 2)
        z_y = np.zeros(x_size * 2)
        z_x[:x_size] = x_t
        z_y[:y_size] = y_t
        return z_x, z_y
    else:
        z_x = np.zeros(y_size * 2)
        z_y = np.zeros(y_size * 2)
        z_x[:x_size] = x_t
        z_y[:y_size] = y_t
        return z_x, z_y

def _convert_correlation(x_t, y_t, mode :str):
    return np.correlate(y_t, x_t, mode)


def _convert_deconvolution(x_t, y_t):
    x_t, y_t = _resizing(x_t, y_t)
    x_f = np.fft.fft(x_t)
    y_f = np.fft.fft(y_t)
    x_f[0] = 1
    h_f = y_f / x_f
    return np.fft.ifft(h_f)


def _convert_wiener_deconv(x_t, y_t, snr_dB):
    x_t, y_t = _resizing(x_t, y_t)
    x_f = np.fft.fft(x_t)
    y_f = np.fft.fft(y_t)
    x_f[0] = 0
    # x_f[0] = 1
    snr = math.pow(10, snr_dB/10)
    g_f = np.conj(x_f) / (np.square(np.absolute(x_f)) + 1 / snr)
    h_f = y_f * g_f
    h_t = np.fft.ifft(h_f)
    h_t = h_t[:h_t.size // 2]
    return h_t


def _convert_filter_lpf_f_all_cut(self, x_t, ff):
    x_f = np.fft.fft(x_t)

    for i in range(ff, x_t.size):
        x_f[i] = 0

    return np.fft.ifft(x_f)