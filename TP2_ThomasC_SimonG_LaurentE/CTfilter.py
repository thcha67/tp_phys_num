#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TP reconstruction TDM (CT)
# Prof: Philippe Després
# programme: Dmitri Matenine (dmitri.matenine.1@ulaval.ca)


# libs
import numpy as np

## filtrer le sinogramme
## ligne par ligne
def filterSinogram(sinogram):
    for i in range(sinogram.shape[0]):
        sinogram[i] = filterLine(sinogram[i])
    return sinogram

## filter une ligne (projection) via FFT
def filterLine(projection):
    fft_proj = np.fft.fft(projection)
    fft_proj = np.fft.fftshift(fft_proj)
    
    freqs = np.fft.fftfreq(len(projection))

    # filtre en rampe
    ramp = np.abs(freqs)
    ramp = 1 - ramp/np.max(ramp)

    # appliquer le filtre
    fft_proj = fft_proj*ramp

    # retourner dans l'espace des fréquences
    fft_proj = np.fft.ifftshift(fft_proj)
    filtered_proj = np.fft.ifft(fft_proj)

    return np.real(filtered_proj)