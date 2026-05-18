#!/usr/bin/env python3
"""
True Muon Peak Landau Fitting Test

Fits the Landau (Moyal) distribution strictly on the actual high-energy cosmic ray muon peak
(e.g., 180 mV to 380 mV) to see the true physical MPVs and their voltage dependence,
completely ignoring the low-energy noise/trigger-pickup peak at 50 mV.
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

def fit_true_muon_mpv(data: np.ndarray, bins: int = 100, range_val = (180, 380)) -> tuple:
    counts, bin_edges = np.histogram(data, bins=bins, range=range_val, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    max_idx = np.argmax(counts)
    mpv_est = bin_centers[max_idx]
    width_est = 30.0
    amp_est = np.max(counts) * width_est * 3.0
    
    try:
        popt, _ = curve_fit(landau_fit_func, bin_centers, counts,
                           p0=[mpv_est, width_est, amp_est],
                           bounds=([150.0, 5.0, 0.0], [380.0, 100.0, np.inf]),
                           maxfev=10000)
        return popt[0], popt
    except Exception as e:
        return mpv_est, None

def analyze_voltage(voltage_str: str, data_dir: str):
    print(f"\n=======================================================")
    print(f"  FITTING TRUE MUON PEAKS AT {voltage_str}")
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
        # Fit strictly on the true high-energy muon peak (180 to 380 mV)
        mpv, popt = fit_true_muon_mpv(amps, bins=100, range_val=(180, 380))
        print(f"  Det {d}: True Muon MPV = {mpv:.2f} mV (width = {popt[1] if popt is not None else 'N/A' :.2f} mV)")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    analyze_voltage("800V", os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'))
    analyze_voltage("850V", os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'))
    analyze_voltage("900V", os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'))

if __name__ == "__main__":
    main()
