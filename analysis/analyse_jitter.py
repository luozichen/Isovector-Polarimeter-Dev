#!/usr/bin/env python3
"""
Cosmic Ray Jitter Analysis with Software Collimation
as per instructions.txt

Usage:
    python3 analyse_jitter.py [data_dir]

The script assumes data_dir contains Tektronix CSV files (Ch1..Ch4).
It attempts to parse the detector mapping from the folder name (e.g. *_config_1234).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, lsq_linear
from scipy.stats import norm
import os
import glob
import sys
import re
import argparse

# --- Configuration ---
# Default thresholds (fallback if auto-detection fails or for initial tuning)
# These are rough guesses based on previous logs (MPV ~100-200mV)
# The script will try to determine these dynamically if requested, 
# but "strict" usually means something like > 50-80 mV to cut the noise tail.
DEFAULT_CUT_THRESHOLD_MV = 50.0 
CFD_FRACTION = 0.3

def parse_detector_mapping(run_dir):
    """
    Extracts detector mapping from folder name.
    Expected format: ..._config_ABCD...
    Where A,B,C,D are detector IDs for Ch1, Ch2, Ch3, Ch4.
    Returns: dict {ch_idx (1-4): det_id (int)}
    """
    dirname = os.path.basename(os.path.normpath(run_dir))
    match = re.search(r'config_(\d{4})', dirname)
    
    mapping = {}
    if match:
        s = match.group(1)
        mapping[1] = int(s[0])
        mapping[2] = int(s[1])
        mapping[3] = int(s[2])
        mapping[4] = int(s[3])
        print(f"Detector Mapping detected from folder: {mapping}")
    else:
        print("WARNING: Could not detect mapping from folder name. Assuming 1-to-1 (1234).")
        mapping = {1:1, 2:2, 3:3, 4:4}
    return mapping

def read_tek_csv(filepath):
    """
    Reads a Tektronix CSV file with stacked frames.
    Returns: time_array, frames_matrix (N_events x N_samples)
    """
    # 1. Parse Metadata
    metadata = {}
    with open(filepath, 'r') as f:
        line1 = f.readline().split(',')
        if "Record Length" in line1[0]:
            metadata['Record Length'] = int(line1[1])
            
    if 'Record Length' not in metadata:
        raise ValueError(f"Could not find 'Record Length' in {filepath}")
    
    record_length = metadata['Record Length']
    
    # 2. Read Data
    # Pandas is fast.
    df = pd.read_csv(filepath, header=None, usecols=[3, 4], names=['Time', 'Volts'])
    
    # 3. Reshape
    total_points = len(df)
    num_frames = total_points // record_length
    
    time = df['Time'].values[:record_length]
    volts = df['Volts'].values[:num_frames * record_length]
    frames = volts.reshape((num_frames, record_length))
    
    return time, frames

def get_dcfd_time(time, waveform, fraction=0.3):
    """
    Digital CFD with linear interpolation.
    Assumes negative pulses.
    """
    # 1. Find Peak (Minimum voltage for negative pulse)
    # Using argmin
    idx_peak = np.argmin(waveform)
    v_peak = waveform[idx_peak]
    
    # Validation: Peak should be significantly negative
    # (This is handled by the Landau Cut step, but good to be safe)
    if v_peak > 0:
        return np.nan # Invalid pulse

    # 2. Target Voltage
    v_target = fraction * v_peak
    
    # 3. Scan Rising Edge (Left of peak)
    # We look backwards from peak or forwards from start? 
    # For a clean cosmic signal, scanning forward from index 0 to idx_peak is standard.
    
    # Find index i such that V[i] > V_target and V[i+1] <= V_target
    # (Remember V is negative, so "rising edge" means voltage is dropping from 0 to negative peak)
    # So we want the crossing point where Voltage goes BELOW V_target.
    
    # Let's search in the region before the peak
    search_region = waveform[:idx_peak]
    
    # Find last point where V > V_target (closer to 0)
    # indices where V > V_target
    candidates = np.where(search_region > v_target)[0]
    
    if len(candidates) == 0:
        return np.nan # Pulse starts below target? (Baseline offset?)

    i = candidates[-1] # The last point above target
    
    if i >= len(search_region) - 1:
        return np.nan # Edge case
        
    # v[i] > v_target
    # v[i+1] <= v_target
    
    t_i = time[i]
    t_next = time[i+1]
    v_i = waveform[i]
    v_next = waveform[i+1]
    
    # 4. Interpolation
    # t = t_i + (t_next - t_i) * (v_target - v_i) / (v_next - v_i)
    slope = (v_next - v_i)
    if slope == 0:
        return t_i
        
    t_interp = t_i + (t_next - t_i) * (v_target - v_i) / slope
    return t_interp

def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def analyze_jitter(run_dir, output_dir):
    run_name = os.path.basename(os.path.normpath(run_dir))
    mapping = parse_detector_mapping(run_dir)
    
    # 1. Data Ingestion
    print("Loading data...")
    csv_files = glob.glob(os.path.join(run_dir, "*_Ch*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return
    
    prefix = os.path.basename(csv_files[0]).split("_Ch")[0]
    
    data = {}
    time = None
    num_events = 0
    
    for ch in range(1, 5):
        pattern = os.path.join(run_dir, f"{prefix}_Ch{ch}.csv")
        files = glob.glob(pattern)
        if not files:
            print(f"Missing Ch{ch}")
            return
        t, frames = read_tek_csv(files[0])
        data[ch] = frames
        if time is None: time = t
        num_events = frames.shape[0]
        
    print(f"Events loaded: {num_events}")
    
    # 2. Amplitude Calculation
    print("Calculating amplitudes...")
    amplitudes = {ch: [] for ch in range(1, 5)}
    for ch in range(1, 5):
        # Min because pulses are negative
        mins = np.min(data[ch], axis=1)
        amplitudes[ch] = np.abs(mins) # Convert to positive magnitude
        
    # 3. Software Collimation (Landau Cut)
    # Determine Cuts
    cuts = {}
    fig_cuts, axes_cuts = plt.subplots(2, 2, figsize=(12, 10))
    axes_cuts = axes_cuts.flatten()
    fig_cuts.suptitle(f"Pulse Height Distributions & Cuts - {run_name}")
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes_cuts[i]
        amps = amplitudes[ch]
        
        # Simple auto-threshold logic:
        # 1. Histogram
        counts, bins, _ = ax.hist(amps, bins=100, range=(0, 0.5), histtype='step', label='Data')
        
        # 2. Find Peak (roughly)
        # Smoothing or simple argmax
        peak_idx = np.argmax(counts)
        peak_val = bins[peak_idx]
        
        # 3. Define Cut: A bit below the peak.
        # Ideally we want to cut the "noise tail" which is usually near 0.
        # But instructions say "strict voltage threshold... just below this peak".
        # Let's say 0.6 * Peak Position? Or a hard value?
        # Let's use a conservative fraction of the peak to be safe, or 50mV, whichever is higher.
        
        cut_val = max(DEFAULT_CUT_THRESHOLD_MV / 1000.0, peak_val * 0.6) 
        cuts[ch] = cut_val
        
        ax.axvline(cut_val, color='r', linestyle='--', label=f'Cut: {cut_val*1000:.1f} mV')
        ax.set_title(f"Ch{ch} (Det {mapping[ch]}) - Peak ~{peak_val*1000:.0f} mV")
        ax.set_xlabel("Amplitude (V)")
        ax.legend()
        
    plt.savefig(os.path.join(output_dir, f"{run_name}_cuts.png"))
    plt.close()
    
    # Filter Events
    clean_indices = []
    for i in range(num_events):
        passed = True
        for ch in range(1, 5):
            if amplitudes[ch][i] < cuts[ch]:
                passed = False
                break
        if passed:
            clean_indices.append(i)
            
    print(f"Software Collimation: Kept {len(clean_indices)} / {num_events} events ({len(clean_indices)/num_events:.1%})")
    
    if len(clean_indices) < 10:
        print("Not enough events passed the cuts. Aborting.")
        return

    # 4. Timing Extraction (dCFD)
    print("Extracting timings...")
    times = {ch: [] for ch in range(1, 5)}
    
    for idx in clean_indices:
        for ch in range(1, 5):
            t_val = get_dcfd_time(time, data[ch][idx], fraction=CFD_FRACTION)
            times[ch].append(t_val)
            
    # Convert to numpy arrays
    for ch in range(1, 5):
        times[ch] = np.array(times[ch])
        
    # 5. Statistical Analysis (Pair Variances)
    pairs = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
    pair_variances = {} # Key: (chA, chB) -> variance
    
    fig_pairs, axes_pairs = plt.subplots(2, 3, figsize=(15, 10))
    axes_pairs = axes_pairs.flatten()
    fig_pairs.suptitle(f"Time Difference Distributions (dCFD {CFD_FRACTION*100:.0f}%)")
    
    pair_variance_vector = [] # For the solver
    
    for i, (chA, chB) in enumerate(pairs):
        ax = axes_pairs[i]
        
        # Difference
        # Valid checks: remove NaNs if dCFD failed
        tA = times[chA]
        tB = times[chB]
        
        # Mask NaNs
        mask = (~np.isnan(tA)) & (~np.isnan(tB))
        delta_t = (tA[mask] - tB[mask]) * 1e9 # Convert to ns
        
        # Fit Gaussian
        mean_guess = np.mean(delta_t)
        std_guess = np.std(delta_t)
        
        # Histogram
        counts, bins, _ = ax.hist(delta_t, bins=30, alpha=0.6, density=True, label='Data')
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts, 
                                p0=[1.0, mean_guess, std_guess], maxfev=5000)
            sigma_pair = abs(popt[2])
            mean_pair = popt[1]
            
            x_plot = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_plot, gaussian(x_plot, *popt), 'r-', label=f'$\sigma$={sigma_pair:.3f} ns')
            
        except Exception as e:
            print(f"Fit failed for pair {chA}-{chB}: {e}. Using raw std.")
            sigma_pair = std_guess
            mean_pair = mean_guess
        
        ax.set_title(f"Ch{chA} - Ch{chB}")
        ax.set_xlabel("$\Delta t$ (ns)")
        ax.legend()
        
        pair_variances[(chA, chB)] = sigma_pair**2
        pair_variance_vector.append(sigma_pair**2)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(output_dir, f"{run_name}_timing_pairs.png"))
    plt.close()
    
    # 6. The Solver (Least Squares)
    # We solve for x_i = sigma_i^2
    # System: x_A + x_B = sigma_AB^2

    # Design Matrix A (6 rows, 4 columns)
    # Columns correspond to Ch1, Ch2, Ch3, Ch4
    A = np.zeros((6, 4))
    Y = np.array(pair_variance_vector)
    
    for i, (chA, chB) in enumerate(pairs):
        # chA is 1-based, index is 0-based
        A[i, chA-1] = 1
        A[i, chB-1] = 1
        
    # Constrained Least Squares? Variances must be positive.
    # scipy.optimize.lsq_linear allows bounds.
    res = lsq_linear(A, Y, bounds=(0, np.inf))
    
    variances = res.x
    jitters = np.sqrt(variances)
    
    print("\n=== Jitter Analysis Results ===")
    print(f"Solver Cost: {res.cost}")
    print("Intrinsic Jitter (sigma):")
    
    results_txt = []
    results_txt.append(f"Run: {run_name}")
    results_txt.append(f"Events: {len(clean_indices)}")
    
    for ch in range(1, 5):
        det_id = mapping[ch]
        sigma_ns = jitters[ch-1]
        line = f"  Ch{ch} (Det {det_id}): {sigma_ns:.3f} ns"
        print(line)
        results_txt.append(line)
        
    # Save text results
    with open(os.path.join(output_dir, f"{run_name}_jitter_results.txt"), "w") as f:
        f.write("\n".join(results_txt))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jitter Analysis")
    parser.add_argument("run_dir", help="Data directory")
    parser.add_argument("--output", "-o", default="results", help="Output directory")
    
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    
    analyze_jitter(args.run_dir, args.output)
