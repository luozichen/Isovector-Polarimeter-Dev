#!/usr/bin/env python3
"""
Dynamic Wide Range True Muon Peak Fitting

Fits the Landau distribution on a dynamic wide range that is tailored to each voltage:
- 800V: (180, 600) mV
- 850V: (200, 700) mV
- 900V: (250, 850) mV

This completely avoids the low-energy noise tail and fits the true physical cosmic ray peaks.
"""

import os
import sys
import numpy as np
import glob
from scipy.optimize import curve_fit

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader
from analysis import config
from analysis.utils.physics import landau_fit_func

def fit_dynamic_mpv(data: np.ndarray, voltage_str: str, bins: int = 100) -> tuple:
    # Set fit range dynamically based on voltage to completely clear the noise tail
    if "800V" in voltage_str:
        fit_range = (180, 600)
    elif "850V" in voltage_str:
        fit_range = (200, 700)
    else:
        fit_range = (250, 850)
        
    counts, bin_edges = np.histogram(data, bins=bins, range=fit_range, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    max_idx = np.argmax(counts)
    mpv_est = bin_centers[max_idx]
    width_est = 35.0
    amp_est = np.max(counts) * width_est * 3.0
    
    try:
        popt, _ = curve_fit(landau_fit_func, bin_centers, counts,
                           p0=[mpv_est, width_est, amp_est],
                           bounds=([fit_range[0], 5.0, 0.0], [fit_range[1], 150.0, np.inf]),
                           maxfev=10000)
        return popt[0], popt
    except Exception as e:
        return mpv_est, None

def analyze_voltage(voltage_str: str, data_dir: str):
    print(f"\n=======================================================")
    print(f"  FITTING DYNAMIC TRUE MUON PEAKS AT {voltage_str}")
    print(f"=======================================================")
    
    if not os.path.exists(data_dir):
        return
        
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    detectors = [1, 3, 5, 6]
    det_amplitudes = {d: [] for d in detectors}
    
    for prefix in sorted(prefixes):
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            continue
            
        pair_id = os.path.basename(prefix).split('_')[-1]
        if len(pair_id) != 2:
            continue
            
        det_top = int(pair_id[0])
        det_bot = int(pair_id[1])
        if det_top == 4 or det_bot == 4:
            continue
            
        try:
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            
            _, volts3 = reader3.read_data(baseline_restore=True)
            _, volts4 = reader4.read_data(baseline_restore=True)
            
            for i in range(volts3.shape[0]):
                if np.max(volts3[i]) > config.POSITIVE_NOISE_THRESHOLD or np.max(volts4[i]) > config.POSITIVE_NOISE_THRESHOLD:
                    continue
                amp3_mV = np.abs(np.min(volts3[i])) * 1000.0
                amp4_mV = np.abs(np.min(volts4[i])) * 1000.0
                
                if det_top in det_amplitudes:
                    det_amplitudes[det_top].append(amp3_mV)
                if det_bot in det_amplitudes:
                    det_amplitudes[det_bot].append(amp4_mV)
                    
        except Exception as e:
            pass
            
    for d in detectors:
        amps = np.array(det_amplitudes[d])
        if len(amps) < 10:
            continue
        mpv, popt = fit_dynamic_mpv(amps, voltage_str, bins=100)
        print(f"  Det {d}: True Muon MPV = {mpv:.2f} mV (width = {popt[1] if popt is not None else 'N/A' :.2f} mV, events: {len(amps)})")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    analyze_voltage("800V", os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'))
    analyze_voltage("850V", os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'))
    analyze_voltage("900V", os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'))

if __name__ == "__main__":
    main()
