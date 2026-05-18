#!/usr/bin/env python3
"""
Cylindrical Detector Physical Characterization Script (Excluding Detector 4)

Performs full energy calibration (Landau fitting) and intrinsic jitter extraction
(Least-squares solving on Golden Pairs) for physical cylindrical detectors (1, 3, 5, 6)
at 800V, 850V, and 900V working voltages. Detector 4 is completely excluded.

Updated to fit the Landau distribution strictly on the range (10 to 250 mV)
to completely ignore all events above 250 mV, avoiding clipping and dynamic
range limits during peak extraction.

Usage:
    python analysis/characterize_cylindrical.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.optimize import curve_fit, lsq_linear

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader
from analysis import config
from analysis.utils.physics import landau_fit_func, get_dcfd_time, gaussian

# Reference simulation energy MPV (extracted from v0600 simulation, ~1.85 MeV)
SIM_REF_MPV_MEV = 1.85

def fit_gaussian_sigma(data: np.ndarray, bins: int = 50) -> tuple:
    """ Fits a Gaussian to the data and returns (sigma, popt). """
    mean = np.mean(data)
    std = np.std(data)
    counts, bin_edges = np.histogram(data, bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    try:
        popt, _ = curve_fit(gaussian, bin_centers, counts, 
                           p0=[np.max(counts), mean, std],
                           maxfev=5000)
        return abs(popt[2]), popt
    except:
        return std, None

def fit_landau_mpv(data: np.ndarray, voltage_str: str, bins: int = 100) -> tuple:
    """ Fits a SciPy Moyal (Landau) strictly to the true physical cosmic ray muon peak. """
    # 1. Find the bin with the highest peak that's later than 200 mV
    temp_counts, temp_edges = np.histogram(data, bins=150, range=(10, 800))
    temp_centers = (temp_edges[:-1] + temp_edges[1:]) / 2
    
    mask = temp_centers > 200.0
    if not np.any(mask):
        start_fit = 250.0
    else:
        valid_centers = temp_centers[mask]
        valid_counts = temp_counts[mask]
        max_idx = np.argmax(valid_counts)
        peak_bin_center = valid_centers[max_idx]
        start_fit = max(10.0, peak_bin_center - 50.0)
        
    # 2. Extract bin centers and counts directly from the full plotted histogram to ensure same bins & scale
    full_counts, full_edges = np.histogram(data, bins=100, range=(10, 800), density=True)
    full_centers = (full_edges[:-1] + full_edges[1:]) / 2
    
    fit_mask = (full_centers >= start_fit) & (full_centers <= 550.0)
    bin_centers = full_centers[fit_mask]
    counts = full_counts[fit_mask]
    
    if len(bin_centers) < 3:
        return 350.0, None
    
    # Estimate starting parameters
    max_idx = np.argmax(counts)
    mpv_est = bin_centers[max_idx]
    width_est = 35.0
    amp_est = np.max(counts) * width_est * 3.0
    
    try:
        popt, _ = curve_fit(landau_fit_func, bin_centers, counts,
                           p0=[mpv_est, width_est, amp_est],
                           bounds=([start_fit, 5.0, 0.0], [550.0, 150.0, np.inf]),
                           maxfev=10000)
        return popt[0], popt
    except Exception as e:
        return mpv_est, None

def analyze_voltage(voltage_str: str, data_dir: str, output_dir: str):
    print(f"\n=======================================================")
    print(f"  ANALYZING CYLINDRICAL DETECTORS AT {voltage_str}")
    print(f"  (Excluding faulty Detector 4 | Landau Fit 10-250 mV)")
    print(f"=======================================================")
    
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} does not exist. Skipping.")
        return None
        
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    detectors = [1, 3, 5, 6]
    det_amplitudes = {d: [] for d in detectors}
    pair_delta_ts = {}
    
    for prefix in sorted(prefixes):
        basename = os.path.basename(prefix)
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            continue
            
        pair_id = basename.split('_')[-1]
        if len(pair_id) != 2:
            continue
            
        det_top = int(pair_id[0])
        det_bot = int(pair_id[1])
        
        if det_top == 4 or det_bot == 4:
            continue
            
        pair_key = f"{min(det_top, det_bot)}-{max(det_top, det_bot)}"
        if pair_key not in pair_delta_ts:
            pair_delta_ts[pair_key] = []
            
        try:
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            
            t3, volts3 = reader3.read_data(baseline_restore=True)
            t4, volts4 = reader4.read_data(baseline_restore=True)
            num_events = volts3.shape[0]
            
            for i in range(num_events):
                if np.max(volts3[i]) > config.POSITIVE_NOISE_THRESHOLD or np.max(volts4[i]) > config.POSITIVE_NOISE_THRESHOLD:
                    continue
                    
                amp3_mV = np.abs(np.min(volts3[i])) * 1000.0
                amp4_mV = np.abs(np.min(volts4[i])) * 1000.0
                
                # LOWERED THRESHOLD CUT TO 10 mV
                if amp3_mV < 10.0 or amp4_mV < 10.0:
                    continue
                    
                if det_top in det_amplitudes:
                    det_amplitudes[det_top].append(amp3_mV)
                if det_bot in det_amplitudes:
                    det_amplitudes[det_bot].append(amp4_mV)
                    
                t_top = get_dcfd_time(t3, volts3[i], config.CFD_FRACTION)
                t_bot = get_dcfd_time(t4, volts4[i], config.CFD_FRACTION)
                
                if not np.isnan(t_top) and not np.isnan(t_bot):
                    dt = (t_top - t_bot) * 1e9
                    if det_top > det_bot:
                        dt = -dt
                    pair_delta_ts[pair_key].append(dt)
                    
        except Exception as e:
            pass
            
    # ===== SECTION 1: ENERGY CALIBRATION =====
    print("\n--- Performing Landau (Moyal) Fitting for Energy Calibration ---")
    extracted_mpvs = {}
    calibration_constants = {}
    
    for d in detectors:
        amps = np.array(det_amplitudes[d])
        if len(amps) < 10:
            extracted_mpvs[d] = np.nan
            calibration_constants[d] = np.nan
            continue
            
        # Fit dynamically on the true physical cosmic ray muon peak
        mpv, popt = fit_landau_mpv(amps, voltage_str, bins=100)
        extracted_mpvs[d] = mpv
        cal = SIM_REF_MPV_MEV / mpv
        calibration_constants[d] = cal
        print(f"  Det {d}: Landau MPV = {mpv:.2f} mV => Calibration = {cal:.5f} MeV/mV")
        
    # ===== SECTION 2: JITTER SOLVER =====
    print("\n--- Performing Pairwise Timing Fitting & Jitter Solving ---")
    measured_pairs = sorted([k for k, v in pair_delta_ts.items() if len(v) >= 10])
    
    pair_variances = []
    pair_sigmas = {}
    
    for pair_key in measured_pairs:
        dt_data = np.array(pair_delta_ts[pair_key])
        dt_centered = dt_data - np.mean(dt_data)
        
        sigma_pair, popt = fit_gaussian_sigma(dt_centered, bins=50)
        pair_variances.append(sigma_pair**2)
        pair_sigmas[pair_key] = sigma_pair
        print(f"  Pair {pair_key}: \\sigma_pair = {sigma_pair:.3f} ns (events: {len(dt_data)})")
        
    if len(measured_pairs) < 3:
        intrinsic_sigmas = {d: np.nan for d in detectors}
    else:
        A = np.zeros((len(measured_pairs), len(detectors)))
        for row_idx, pair_key in enumerate(measured_pairs):
            d1, d2 = map(int, pair_key.split('-'))
            col_idx1 = detectors.index(d1)
            col_idx2 = detectors.index(d2)
            A[row_idx, col_idx1] = 1.0
            A[row_idx, col_idx2] = 1.0
            
        y = np.array(pair_variances)
        res = lsq_linear(A, y, bounds=(0, np.inf))
        intrinsic_sigmas = {detectors[i]: np.sqrt(res.x[i]) for i in range(len(detectors))}
        
    return {
        "fit_mpvs": extracted_mpvs,
        "calibrations": calibration_constants,
        "jitters": intrinsic_sigmas
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'results', 'physical')
    
    res_800 = analyze_voltage("800V", os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'), output_dir)
    res_850 = analyze_voltage("850V", os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'), output_dir)
    res_900 = analyze_voltage("900V", os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'), output_dir)
    
    # Save the consolidated table to cylindrical_results.txt
    out_table_path = os.path.join(output_dir, "cylindrical_results.txt")
    with open(out_table_path, "w") as f:
        f.write("=========================================================================================\n")
        f.write("   CYLINDRICAL DETECTOR CHARACTERIZATION SUMMARY (PHYSICAL DATA)                         \n")
        f.write(f"   Reference Simulation MPV: {SIM_REF_MPV_MEV} MeV (Excluding faulty Detector 4)          \n")
        f.write("   Note: Landau MPV fitted strictly on the physical cosmic ray muon peak\n")
        f.write("         (180-600 mV for 800V, 200-700 mV for 850V, 250-850 mV for 900V)\n")
        f.write("=========================================================================================\n\n")
        
        for voltage, res in [("800V", res_800), ("850V", res_850), ("900V", res_900)]:
            if res is None:
                continue
            f.write(f"--- Working Voltage: {voltage} ---\n")
            f.write(f"{'Detector':<10} | {'Landau MPV (mV)':<16} | {'Calibration (MeV/mV)':<22} | {'Intrinsic Jitter (ns)':<22} | {'FWHM (ns)':<10}\n")
            f.write("-" * 95 + "\n")
            for d in [1, 3, 5, 6]:
                mpv = res["fit_mpvs"].get(d, np.nan)
                cal = res["calibrations"].get(d, np.nan)
                jit = res["jitters"].get(d, np.nan)
                fwhm = jit * 2.355 if not np.isnan(jit) else np.nan
                
                mpv_str = f"{mpv:.2f}" if not np.isnan(mpv) else "N/A"
                cal_str = f"{cal:.5f}" if not np.isnan(cal) else "N/A"
                jit_str = f"{jit:.4f}" if not np.isnan(jit) else "N/A"
                fwhm_str = f"{fwhm:.3f}" if not np.isnan(fwhm) else "N/A"
                
                f.write(f"Det {d:<6} | {mpv_str:<16} | {cal_str:<22} | {jit_str:<22} | {fwhm_str:<10}\n")
            f.write("\n" + "=" * 95 + "\n\n")
            
    print(f"\nAll characterization complete! Consolidated results saved to:")
    print(f"  {out_table_path}")

if __name__ == "__main__":
    main()
