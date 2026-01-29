#!/usr/bin/env python3
"""
Physical Data Analysis (Jitter & Software Collimation)
Uses WFM files. 
Updated to handle runXYZ_ABC_DEFG_JKL naming and dynamic Landau ranges/bounds.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, lsq_linear
from scipy.stats import moyal
import os
import glob
import re
import sys
from wfm_reader import WfmReader

# --- Global Configuration (Easily Editable) ---
RESULTS_DIR = "results/physical"
DEFAULT_CUT_THRESHOLD_MV = 50.0 
CFD_FRACTION = 0.3
POSITIVE_NOISE_THRESHOLD = 0.03 # 30 mV (Reject events with positive spikes)

# Landau Plotting & Fitting Defaults
DEFAULT_LANDAU_BINS = 50  # Reverted to 50 for consistency with older runs
DEFAULT_LOWER_BOUND = 0.01 # Standard lower bound for previous consistency

def get_run_config(run_num):
    """
    Returns (lower_bound, max_range, bins) based on the run number.
    Edit this function to customize specific run sets.
    """
    # Default settings for most runs
    lower = DEFAULT_LOWER_BOUND
    upper = 0.4
    bins = DEFAULT_LANDAU_BINS # Default 50
    
    if 2 <= run_num <= 7:
        upper = 0.4
        bins = 50
    elif run_num >= 17:
        # Customizing for run 17 onwards
        lower = 0.2
        upper = 0.6
        bins = 100 # Increased bins only for high-range runs
        
    return lower, upper, bins

# --- Math Functions ---

def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

# --- Logic & Processing ---

def parse_run_info(run_dir):
    """
    Extracts run ID, run number, type (config/det), and detector stack configuration.
    Naming: runXYZ_ABC_DEFG_JKL_...
    """
    dirname = os.path.basename(os.path.normpath(run_dir))
    parts = dirname.split('_')
    
    # Run ID (e.g. run001)
    run_id = parts[0] if len(parts) > 0 else "unknown"
    
    # Extract Run Number for range logic
    run_match = re.search(r'run(\d+)', run_id)
    run_num = int(run_match.group(1)) if run_match else 0
    
    # DEFG segment: config or det
    run_type = parts[2].lower() if len(parts) > 2 else ""
    
    # JKL segment: Stack Configuration (e.g. 1234)
    config_str = parts[3] if len(parts) > 3 else "1234"
        
    return run_id, run_num, run_type, config_str

def get_position_label(det_id, config_str):
    """
    Returns the physical position label (Top, Mid1, Mid2, Bot) 
    for a given Detector ID (1-4) based on the config string.
    """
    det_char = str(det_id)
    if det_char not in config_str:
        return "Unknown"
    
    idx = config_str.index(det_char)
    positions = ["Top", "Mid1", "Mid2", "Bot"]
    if idx < len(positions):
        return positions[idx]
    return "Unknown"

def load_wfm_data(run_dir):
    """
    Loads WFM data from a run directory.
    """
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files:
        return None, None

    # Group by prefix
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
    
    data = {}
    time = None
    num_events = 0
    
    for ch in range(1, 5):
        if ch not in file_map:
            print(f"  Missing Ch{ch} in {run_dir}")
            return None, None
            
        wfm = WfmReader(file_map[ch])
        t, v = wfm.read_data()
        data[ch] = v
        
        if time is None: time = t
        
        if num_events == 0: num_events = wfm.num_frames
        elif num_events != wfm.num_frames:
            num_events = min(num_events, wfm.num_frames)
            
    # Truncate
    for ch in data:
        data[ch] = data[ch][:num_events]
        
    return time, data

def get_dcfd_time(time, waveform, fraction=0.3):
    """
    Digital CFD with linear interpolation.
    """
    # 1. Find Peak
    idx_peak = np.argmin(waveform)
    v_peak = waveform[idx_peak]
    
    if v_peak > 0: return np.nan 

    # 2. Target Voltage
    v_target = fraction * v_peak
    
    # 3. Scan Rising Edge
    search_region = waveform[:idx_peak]
    candidates = np.where(search_region > v_target)[0]
    
    if len(candidates) == 0: return np.nan

    i = candidates[-1]
    
    if i >= len(search_region) - 1: return np.nan
        
    t_i = time[i]
    t_next = time[i+1]
    v_i = waveform[i]
    v_next = waveform[i+1]
    
    # 4. Interpolation
    slope = (v_next - v_i)
    if slope == 0: return t_i
        
    t_interp = t_i + (t_next - t_i) * (v_target - v_i) / slope
    return t_interp

def plot_waveforms(time, data, indices, run_id, label, suffix):
    """
    Generic waveform plotter.
    """
    if not indices: return

    indices_to_plot = indices[:5]
    n = len(indices_to_plot)
    
    fig, axes = plt.subplots(n, 1, figsize=(10, 3*n), sharex=True)
    if n == 1: axes = [axes]
    
    fig.suptitle(f"{run_id} - {label}", fontsize=16)
    
    for i, idx in enumerate(indices_to_plot):
        ax = axes[i]
        for ch in range(1, 5):
            ax.plot(time*1e9, data[ch][idx]*1000, label=f"Ch{ch}")
        
        ax.set_title(f"Event #{idx}")
        ax.set_ylabel("mV")
        ax.grid(True, alpha=0.3)
        if i == 0: ax.legend(loc='upper right')
        
    axes[-1].set_xlabel("Time (ns)")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(RESULTS_DIR, f"{run_id}_{suffix}.png")
    plt.savefig(out_path)
    plt.close(fig)
    print(f"  Saved {suffix}: {out_path}")

def plot_landau_fits(amplitudes, cuts, run_id, config_str, landau_range, bins_count):
    """
    Plots Pulse Height Distributions with Landau Fits using specific max range.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    fig.suptitle(f"{run_id} (Config {config_str}) - Energy Deposition")
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes[i]
        vals = np.array(amplitudes[ch])
        
        # Histogram
        y, x, _ = ax.hist(vals, bins=bins_count, range=landau_range, 
                          density=False, histtype='stepfilled', alpha=0.4, label='Data')
        
        bin_centers = (x[:-1] + x[1:]) / 2
        
        # Fit
        if len(vals) > 0 and np.max(y) > 0:
            peak_idx = np.argmax(y)
            mpv_guess = bin_centers[peak_idx]
            try:
                # Ensure we don't restrict standard runs more than original (bound was 1.0)
                # while allowing high-voltage runs to have a higher MPV limit.
                mpv_limit = max(1.0, landau_range[1] * 1.2)
                popt, _ = curve_fit(landau_fit_func, bin_centers, y, 
                                    p0=[mpv_guess, 0.01, np.max(y)*0.01], 
                                    bounds=([0, 0, 0], [mpv_limit, 1, np.inf]))
                
                x_fine = np.linspace(landau_range[0], landau_range[1], 200)
                ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'r-', lw=2, 
                        label=f'Fit\nMPV={popt[0]*1000:.1f} mV')
            except Exception as e:
                print(f"  [Warning] Ch{ch} fit failed: {e}")
            
        cut_val = cuts[ch]
        ax.axvline(cut_val, color='k', linestyle='--', label=f'Cut: {cut_val*1000:.1f} mV')
        
        det_id = ch
        pos_label = get_position_label(det_id, config_str)
        ax.set_title(f"Ch{ch} - Det {det_id} [{pos_label}]")
        ax.set_xlabel("Amplitude (V)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(RESULTS_DIR, f"{run_id}_landau_fits.png")
    plt.savefig(out_path)
    plt.close(fig)
    print(f"  Saved landau fits: {out_path}")

def analyze_run(run_dir):
    run_id, run_num, run_type, config_str = parse_run_info(run_dir)
    
    # Only analyze if segment DEFG is 'config'
    if run_type != "config":
        return

    # Get dynamic range, lower bound, and bins from config at top of file
    low_bound, max_range, bins_count = get_run_config(run_num)
    landau_range = (low_bound, max_range)
    
    print(f"Analyzing: {run_id} (Range: {low_bound}-{max_range}V, Bins: {bins_count})")
    
    time, data = load_wfm_data(run_dir)
    if data is None:
        print("  Skipping run (incomplete channels or load error).")
        return

    num_events = data[1].shape[0]
    print(f"  Events: {num_events}")
    
    # --- Amplitude Calculation ---
    amplitudes = {ch: np.abs(np.min(data[ch], axis=1)) for ch in range(1, 5)}
    
    # --- Define Cuts ---
    cuts = {}
    for ch in range(1, 5):
        amps = amplitudes[ch]
        # Keep original logic: histogram at range (0, 0.5) to find peak for cuts
        counts, bins = np.histogram(amps, bins=100, range=(0, 0.5))
        bin_centers = (bins[:-1] + bins[1:]) / 2
        peak_idx = np.argmax(counts)
        peak_val = bin_centers[peak_idx]
        cut_val = max(DEFAULT_CUT_THRESHOLD_MV / 1000.0, peak_val * 0.9)
        cuts[ch] = cut_val
        
    # --- Categorize Events ---
    clean_indices = []
    clipped_indices = []
    noise_indices = []
    
    for i in range(num_events):
        # 1. Check Electronic Noise (Positive Excursion)
        is_electronic_noise = False
        for ch in range(1, 5):
            if np.max(data[ch][i]) > POSITIVE_NOISE_THRESHOLD:
                is_electronic_noise = True
                break
        
        if is_electronic_noise:
            noise_indices.append(i)
            continue
            
        # 2. Check Clipping (Low Amplitude)
        is_clipped = False
        for ch in range(1, 5):
            if amplitudes[ch][i] < cuts[ch]:
                is_clipped = True
                break
                
        if is_clipped:
            clipped_indices.append(i)
        else:
            clean_indices.append(i)
            
    print(f"  Clean: {len(clean_indices)} ({len(clean_indices)/num_events:.1%})")
    print(f"  Clipped (Low Energy): {len(clipped_indices)}")
    print(f"  Electronic Noise: {len(noise_indices)}")
    
    # --- Plots ---
    valid_indices = sorted(clean_indices + clipped_indices)
    amplitudes_valid = {ch: amplitudes[ch][valid_indices] for ch in range(1, 5)}
    
    plot_landau_fits(amplitudes_valid, cuts, run_id, config_str, landau_range, bins_count)
    
    if clean_indices:
        plot_waveforms(time, data, clean_indices, run_id, "Good Waveforms", "good_waveforms")
    
    if clipped_indices:
        plot_waveforms(time, data, clipped_indices, run_id, "Clipped / Low Energy Events", "clipped_check")
        
    if noise_indices:
        plot_waveforms(time, data, noise_indices, run_id, "Electronic Noise (>30mV Positive)", "noise_check")
    
    if len(clean_indices) < 10:
        print("  Not enough clean events for jitter analysis.")
        return

    # --- Timing ---
    print("  Extracting timings...")
    times = {ch: [] for ch in range(1, 5)}
    for idx in clean_indices:
        for ch in range(1, 5):
            times[ch].append(get_dcfd_time(time, data[ch][idx], CFD_FRACTION))
            
    for ch in range(1, 5):
        times[ch] = np.array(times[ch])

    # --- Pairs & Jitter ---
    pairs = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
    
    fig_pairs, axes_pairs = plt.subplots(2, 3, figsize=(15, 10))
    axes_pairs = axes_pairs.flatten()
    fig_pairs.suptitle(f"{run_id} - Time Differences (Clean Events)")
    
    pair_vars = []
    
    for i, (chA, chB) in enumerate(pairs):
        ax = axes_pairs[i]
        tA = times[chA]
        tB = times[chB]
        mask = (~np.isnan(tA)) & (~np.isnan(tB))
        delta_t = (tA[mask] - tB[mask]) * 1e9 # ns
        
        mean = np.mean(delta_t)
        std = np.std(delta_t)
        
        # Gaussian Fit
        counts, bins, _ = ax.hist(delta_t, bins=30, alpha=0.6, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        sigma = std
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts, p0=[1.0, mean, std])
            sigma = abs(popt[2])
            x_fine = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'r-', lw=2)
        except:
            pass
            
        pair_vars.append(sigma**2)
        ax.set_title(f"Ch{chA}-Ch{chB} (Det {chA}-{chB})\nSigma = {sigma:.3f} ns")
        ax.set_xlabel("Delta T (ns)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(RESULTS_DIR, f"{run_id}_timing_pairs.png"))
    plt.close()
    
    # --- Solver ---
    A = np.array([
        [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1], 
        [0, 1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 1]
    ])
    y = np.array(pair_vars)
    res = lsq_linear(A, y, bounds=(0, np.inf))
    sigmas = np.sqrt(res.x)
    
    # --- Save Results to Text (Original Format) ---
    with open(os.path.join(RESULTS_DIR, f"{run_id}_jitter_results.txt"), "w") as f:
        f.write(f"Run: {run_id}\n")
        f.write(f"Config: {config_str}\n")
        f.write(f"Events: {num_events}\n")
        f.write(f"  Clean: {len(clean_indices)}\n")
        f.write(f"  Clipped: {len(clipped_indices)}\n")
        f.write(f"  Noise: {len(noise_indices)}\n")
        f.write("Jitter Results (sigma):\n")
        for i, s in enumerate(sigmas):
            det_id = i + 1
            pos_label = get_position_label(det_id, config_str)
            f.write(f"  Det {det_id} (Ch{i+1}) [{pos_label}]: {s:.4f} ns\n")

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    data_root = "data"
    all_items = sorted(glob.glob(os.path.join(data_root, "run*")))
    run_dirs = [d for d in all_items if os.path.isdir(d)]
    
    for run_dir in run_dirs:
        analyze_run(run_dir)

if __name__ == "__main__":
    main()