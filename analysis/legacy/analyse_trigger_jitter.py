#!/usr/bin/env python3
"""
Trigger Jitter Analysis (Runs 002-007)
Method 3: Direct variation of signal timing w.r.t Trigger.
Assumes Trigger is the "True Signal" timing.
Calculates std(t_CFD) for Middle detectors.

Refactored to use the analysis.utils library.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import sys
import glob
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import config
from analysis.utils.wfm import WfmReader
from analysis.utils.physics import gaussian, get_dcfd_time


# --- Configuration ---
RUN_PATTERN = "run00[2-7]*" 
POSITIVE_NOISE_THRESHOLD = config.POSITIVE_NOISE_THRESHOLD


def parse_run_info(run_dir):
    """Extract run ID and config string from directory name."""
    dirname = os.path.basename(os.path.normpath(run_dir))
    match = re.search(r'config_(\d{4})', dirname)
    config_str = match.group(1) if match else "1234"
    run_id = dirname.split("_")[0]
    return run_id, config_str


def get_middle_detectors(config_str):
    """Get the middle two detectors from config string (positions 1 and 2)."""
    if len(config_str) != 4:
        return []
    return [int(config_str[1]), int(config_str[2])]


def load_run_data(run_dir, target_dets):
    """
    Load waveform data and extract timing for target detectors.
    
    Args:
        run_dir: Path to run directory
        target_dets: List of detector IDs to extract timing for
        
    Returns:
        Dict mapping detector ID to list of timing values
    """
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files:
        return None

    # Group files by prefix
    sets = {}
    for f in wfm_files:
        basename = os.path.basename(f)
        parts = basename.split("_Ch")
        if len(parts) != 2:
            continue
        prefix = parts[0]
        ch = int(parts[1].split(".")[0])
        if prefix not in sets:
            sets[prefix] = {}
        sets[prefix][ch] = f
        
    if not sets:
        return None
    
    prefix = list(sets.keys())[0]
    file_map = sets[prefix]
    
    raw_data = {}
    time = None
    num_events = 0
    
    for ch in range(1, 5):
        if ch not in file_map:
            return None
        wfm = WfmReader(file_map[ch])
        t, v = wfm.read_data()
        raw_data[ch] = v
        if time is None:
            time = t
        if num_events == 0:
            num_events = wfm.num_frames
        else:
            num_events = min(num_events, wfm.num_frames)
    
    # Truncate to consistent event count
    for ch in raw_data:
        raw_data[ch] = raw_data[ch][:num_events]
        
    extracted_times = {det: [] for det in target_dets}
    
    for i in range(num_events):
        # Noise Check (Global)
        is_noise = False
        for ch in range(1, 5):
            if np.max(raw_data[ch][i]) > POSITIVE_NOISE_THRESHOLD:
                is_noise = True
                break
        if is_noise:
            continue
        
        # Extract timing for target detectors
        for det_id in target_dets:
            t_val = get_dcfd_time(time, raw_data[det_id][i], config.CFD_FRACTION)
            extracted_times[det_id].append(t_val)
            
    return extracted_times


def main():
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    run_dirs = sorted(glob.glob(os.path.join(config.DATA_DIR, RUN_PATTERN)))
    
    # Store results for plotting
    plot_data = []
    
    print(f"Analyzing {len(run_dirs)} runs...")
    
    results_txt = []
    results_txt.append("Trigger Jitter Analysis (Method 3)")
    results_txt.append(f"{ 'Run':<8} | { 'Det':<4} | { 'Sigma (ns)':<10}")
    results_txt.append("-" * 30)

    for run_dir in run_dirs:
        run_id, config_str = parse_run_info(run_dir)
        mid_dets = get_middle_detectors(config_str)
        print(f"Processing {run_id} ({config_str}) -> Middle: {mid_dets}")
        
        times_map = load_run_data(run_dir, mid_dets)
        
        if not times_map:
            print("  No data.")
            continue
            
        for det_id in mid_dets:
            times = np.array(times_map[det_id])
            times = times[~np.isnan(times)]
            
            if len(times) < 10:
                print(f"  Det {det_id}: Not enough data.")
                continue
                
            # Calculate std dev wrt trigger
            # std(t) removes the mean offset, giving jitter wrt trigger
            sigma = np.std(times) * 1e9  # ns
            print(f"  Det {det_id}: Sigma = {sigma:.4f} ns")
            
            results_txt.append(f"{run_id:<8} | {det_id:<4} | {sigma:.4f}")
            plot_data.append((run_id, det_id, sigma, times * 1e9))

    # --- Plotting ---
    n_plots = len(plot_data)
    if n_plots == 0:
        print("No data to plot.")
        return
        
    cols = 2
    rows = (n_plots + 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(12, 3 * rows))
    axes = axes.flatten()
    fig.suptitle("Trigger Jitter Distributions (Middle Detectors)\n"
                 "Sigma of Signal Arrival Time w.r.t Trigger", fontsize=16)
    
    for i, (run_id, det_id, sigma, times) in enumerate(plot_data):
        ax = axes[i]
        
        # Center around mean for plotting
        t_centered = times - np.mean(times)
        
        counts, bins, _ = ax.hist(t_centered, bins=40, alpha=0.6, 
                                   density=True, color='purple')
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Fit Gaussian
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts, 
                               p0=[np.max(counts), 0, sigma])
            x_fine = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'k--', lw=1.5, label='Fit')
            fit_sigma = abs(popt[2])
            ax.set_title(f"{run_id} Det {det_id}\n"
                        f"Std: {sigma:.3f} ns | Fit: {fit_sigma:.3f} ns")
        except:
            ax.set_title(f"{run_id} Det {det_id}\n"
                        f"Std: {sigma:.3f} ns (Fit Failed)")
            
        ax.set_xlabel("Time Deviation (ns)")
        ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(config.RESULTS_DIR, "trigger_jitter_histograms.png")
    plt.savefig(out_path)
    print(f"Saved plot to {out_path}")
    
    # Save Text Results
    txt_path = os.path.join(config.RESULTS_DIR, "trigger_jitter_results.txt")
    with open(txt_path, "w") as f:
        f.write("\n".join(results_txt))
    print(f"Saved results to {txt_path}")


if __name__ == "__main__":
    main()
