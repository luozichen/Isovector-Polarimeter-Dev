#!/usr/bin/env python3
"""
Combined Jitter Analysis (Runs 002-007)
Uses "Golden" middle detector pairs to solve for intrinsic detector jitter.
System: 6 Equations (Pairs), 4 Unknowns (Detectors).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, lsq_linear
import os
import glob
import re
from wfm_reader import WfmReader

# --- Configuration ---
RESULTS_DIR = "results/physical"
RUN_PATTERN = "run00[2-7]*" 
POSITIVE_NOISE_THRESHOLD = 0.03 # 30 mV
CFD_FRACTION = 0.3

def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def parse_run_info(run_dir):
    dirname = os.path.basename(os.path.normpath(run_dir))
    match = re.search(r'config_(\d{4})', dirname)
    config_str = match.group(1) if match else "1234"
    run_id = dirname.split("_")[0]
    return run_id, config_str

def get_middle_pair(config_str):
    """
    Returns the tuple of detector IDs (integers) in the middle positions.
    """
    if len(config_str) != 4: return None
    return (int(config_str[1]), int(config_str[2]))

def get_dcfd_time(time, waveform, fraction=0.3):
    """
    Digital CFD with linear interpolation.
    """
    idx_peak = np.argmin(waveform)
    v_peak = waveform[idx_peak]
    
    if v_peak > 0: return np.nan 

    v_target = fraction * v_peak
    
    # Scan Rising Edge
    search_region = waveform[:idx_peak]
    candidates = np.where(search_region > v_target)[0]
    
    if len(candidates) == 0: return np.nan

    i = candidates[-1]
    if i >= len(search_region) - 1: return np.nan
        
    t_i = time[i]
    t_next = time[i+1]
    v_i = waveform[i]
    v_next = waveform[i+1]
    
    slope = (v_next - v_i)
    if slope == 0: return t_i
        
    t_interp = t_i + (t_next - t_i) * (v_target - v_i) / slope
    return t_interp

def load_run_data(run_dir, target_dets):
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files: return None, None

    sets = {}
    for f in wfm_files:
        basename = os.path.basename(f)
        parts = basename.split("_Ch")
        if len(parts) != 2: continue
        prefix = parts[0]
        ch = int(parts[1].split(".")[0])
        if prefix not in sets: sets[prefix] = {}
        sets[prefix][ch] = f
        
    if not sets: return None, None
    prefix = list(sets.keys())[0]
    file_map = sets[prefix]
    
    raw_data = {}
    time = None
    num_events = 0
    
    for ch in range(1, 5):
        if ch not in file_map: return None, None
        wfm = WfmReader(file_map[ch])
        t, v = wfm.read_data()
        raw_data[ch] = v
        if time is None: time = t
        if num_events == 0: num_events = wfm.num_frames
        else: num_events = min(num_events, wfm.num_frames)
    
    for ch in raw_data:
        raw_data[ch] = raw_data[ch][:num_events]
        
    # Extract times for target detectors ONLY if event is clean
    extracted_times = {det: [] for det in target_dets}
    
    for i in range(num_events):
        # Noise Check (Global)
        is_noise = False
        for ch in range(1, 5):
            if np.max(raw_data[ch][i]) > POSITIVE_NOISE_THRESHOLD:
                is_noise = True
                break
        if is_noise: continue
        
        # Calculate Time for target detectors
        for det_id in target_dets:
            # Note: channel = detector id in our setup
            t_val = get_dcfd_time(time, raw_data[det_id][i], CFD_FRACTION)
            extracted_times[det_id].append(t_val)
            
    return np.array(extracted_times[target_dets[0]]), np.array(extracted_times[target_dets[1]])

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    data_root = "data"
    run_dirs = sorted(glob.glob(os.path.join(data_root, RUN_PATTERN)))
    
    # Linear System Matrices
    # A * [s1^2, s2^2, s3^2, s4^2] = [s_pair^2]
    A_matrix = []
    B_vector = []
    
    # Plotting
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    fig.suptitle("Time Difference Distributions (Golden Middle Pairs)", fontsize=16)
    
    plot_idx = 0
    
    print(f"Analyzing {len(run_dirs)} runs...")
    
    for run_dir in run_dirs:
        run_id, config_str = parse_run_info(run_dir)
        detA, detB = get_middle_pair(config_str)
        print(f"Processing {run_id} ({config_str}) -> Pair: {detA}-{detB}")
        
        tA, tB = load_run_data(run_dir, (detA, detB))
        
        if tA is None or len(tA) == 0:
            print("  No valid data found.")
            continue
            
        # Calculate Delta T
        # Remove NaNs (failed CFD)
        valid_mask = (~np.isnan(tA)) & (~np.isnan(tB))
        tA = tA[valid_mask]
        tB = tB[valid_mask]
        
        delta_t = (tA - tB) * 1e9 # ns
        
        # Fit Gaussian to find Sigma_pair
        ax = axes[plot_idx]
        mean = np.mean(delta_t)
        std = np.std(delta_t)
        
        counts, bins, _ = ax.hist(delta_t, bins=40, alpha=0.6, density=True, color='teal')
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        sigma_pair = std
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts, p0=[np.max(counts), mean, std])
            sigma_pair = abs(popt[2])
            x_fine = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'r-', lw=2)
            ax.set_title(f"{run_id}: Det {detA} vs {detB}\nSigma = {sigma_pair:.3f} ns")
        except:
            ax.set_title(f"{run_id}: Det {detA} vs {detB}\nFit Failed")
            print("  Fit failed, using std dev.")
            
        ax.set_xlabel("Delta T (ns)")
        ax.grid(True, alpha=0.3)
        plot_idx += 1
        
        # Add to Linear System
        # Row for A: [is_1, is_2, is_3, is_4]
        row = [0, 0, 0, 0]
        row[detA - 1] = 1
        row[detB - 1] = 1
        
        A_matrix.append(row)
        B_vector.append(sigma_pair**2)
        print(f"  Sigma_pair: {sigma_pair:.4f} ns")

    # Solve System
    print("\nSolving Least Squares System...")
    A = np.array(A_matrix)
    y = np.array(B_vector)
    
    # Solve subject to x >= 0 (variance cannot be negative)
    res = lsq_linear(A, y, bounds=(0, np.inf))
    
    sigmas_squared = res.x
    sigmas = np.sqrt(sigmas_squared)
    
    print("-" * 30)
    print("Intrinsic Jitter Results (sigma):")
    for i, s in enumerate(sigmas):
        print(f"  Detector {i+1}: {s:.4f} ns")
    print("-" * 30)

    # --- Validation ---
    print("\nValidation (Measured vs Predicted):")
    validation_lines = []
    validation_lines.append("\nValidation (Measured vs Predicted):")
    validation_lines.append(f"{'Pair':<10} | {'Measured (ns)':<15} | {'Predicted (ns)':<15} | {'Diff (ns)':<15}")
    validation_lines.append("-" * 65)
    print(validation_lines[-2])
    print(validation_lines[-1])

    y_pred = A @ sigmas_squared
    sigma_pair_pred = np.sqrt(y_pred)
    
    # Map row index back to pair info (we need to store this during the loop)
    # Re-parsing A_matrix to get pair indices
    for idx, row in enumerate(A):
        det_indices = np.where(row == 1)[0]
        detA = det_indices[0] + 1
        detB = det_indices[1] + 1
        
        meas = np.sqrt(y[idx])
        pred = sigma_pair_pred[idx]
        diff = meas - pred
        
        line = f"Det {detA}-{detB:<4} | {meas:.4f}          | {pred:.4f}          | {diff:+.4f}"
        print(line)
        validation_lines.append(line)

    # Save Plot
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(RESULTS_DIR, "combined_jitter_golden.png"))
    
    # Save Text Results
    with open(os.path.join(RESULTS_DIR, "combined_jitter_results.txt"), "w") as f:
        f.write("Combined Intrinsic Jitter Analysis (Runs 002-007)\n")
        f.write("Method: Pairwise Variance of Middle Detectors (Golden Events)\n")
        f.write("-" * 40 + "\n")
        for i, s in enumerate(sigmas):
            f.write(f"Detector {i+1}: {s:.4f} ns\n")
        
        for line in validation_lines:
            f.write(line + "\n")

if __name__ == "__main__":
    main()
