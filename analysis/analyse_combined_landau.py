#!/usr/bin/env python3
"""
Combined Landau Analysis (Runs 002-007)
Grid visualization: 4 Detectors x (3 Individual Runs + 1 Combined)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import moyal
import os
import glob
import re
from wfm_reader import WfmReader

# --- Configuration ---
RESULTS_DIR = "results/physical"
RUN_PATTERN = "run00[2-7]*" 
POSITIVE_NOISE_THRESHOLD = 0.03 # 30 mV
LANDAU_RANGE = (0.01, 0.4)
BINS = 50 

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def parse_run_info(run_dir):
    dirname = os.path.basename(os.path.normpath(run_dir))
    match = re.search(r'config_(\d{4})', dirname)
    config_str = match.group(1) if match else "1234"
    run_id = dirname.split("_")[0]
    return run_id, config_str

def get_middle_detectors(config_str):
    if len(config_str) != 4: return []
    return [int(config_str[1]), int(config_str[2])]

def load_run_data(run_dir, target_dets):
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files: return {}

    sets = {}
    for f in wfm_files:
        basename = os.path.basename(f)
        parts = basename.split("_Ch")
        if len(parts) != 2: continue
        prefix = parts[0]
        ch = int(parts[1].split(".")[0])
        if prefix not in sets: sets[prefix] = {}
        sets[prefix][ch] = f
        
    if not sets: return {}
    prefix = list(sets.keys())[0]
    file_map = sets[prefix]
    
    raw_data = {}
    num_events = 0
    for ch in range(1, 5):
        if ch not in file_map: return {}
        wfm = WfmReader(file_map[ch])
        _, v = wfm.read_data()
        raw_data[ch] = v
        if num_events == 0: num_events = wfm.num_frames
        else: num_events = min(num_events, wfm.num_frames)
    
    for ch in raw_data:
        raw_data[ch] = raw_data[ch][:num_events]
        
    amplitudes = {ch: np.abs(np.min(raw_data[ch], axis=1)) for ch in range(1, 5)}
    clean_amplitudes = {det: [] for det in target_dets}
    
    for i in range(num_events):
        # Noise Check (same as analyse_physical.py)
        is_noise = False
        for ch in range(1, 5):
            if np.max(raw_data[ch][i]) > POSITIVE_NOISE_THRESHOLD:
                is_noise = True
                break
        if is_noise: continue
        
        for det_id in target_dets:
            clean_amplitudes[det_id].append(amplitudes[det_id][i])
            
    return clean_amplitudes

def fit_and_plot(ax, data, label, color):
    if len(data) == 0:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center')
        return None

    y, x, _ = ax.hist(data, bins=BINS, range=LANDAU_RANGE, 
                      density=False, histtype='stepfilled', alpha=0.4, label='Data', color=color)
    
    bin_centers = (x[:-1] + x[1:]) / 2
    
    if len(data) > 0 and np.max(y) > 0:
        peak_idx = np.argmax(y)
        mpv_guess = bin_centers[peak_idx]
        
        # Initial guesses from analyse_physical.py
        p0 = [mpv_guess, 0.01, np.max(y)*0.01] 
        
        try:
            popt, _ = curve_fit(landau_fit_func, bin_centers, y, 
                                p0=p0, 
                                bounds=([0, 0, 0], [1, 1, np.inf]))
            
            x_fine = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 200)
            ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=1.5)
            
            mpv_val = popt[0] * 1000
            print(f"  - Fit Success: {label} | MPV: {mpv_val:.2f} mV")
            ax.text(0.95, 0.95, f"MPV: {mpv_val:.1f} mV\nN: {len(data)}", 
                    transform=ax.transAxes, ha='right', va='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
            return mpv_val
        except:
            print(f"  - Fit Failed: {label}")
            ax.text(0.95, 0.95, f"Fit Failed\nN: {len(data)}", 
                    transform=ax.transAxes, ha='right', va='top', fontsize=9, color='red')
            return None
    return None

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    data_root = "data"
    run_dirs = sorted(glob.glob(os.path.join(data_root, RUN_PATTERN)))
    
    # Store data: detector_data[det_id] = [(run_id, [amps]), ...]
    detector_data = {1: [], 2: [], 3: [], 4: []}
    
    print(f"Found {len(run_dirs)} runs matching {RUN_PATTERN}")
    
    for run_dir in run_dirs:
        run_id, config_str = parse_run_info(run_dir)
        mid_dets = get_middle_detectors(config_str)
        print(f"Processing {run_id} (Config: {config_str}) -> Middle Dets: {mid_dets}")
        
        run_data = load_run_data(run_dir, mid_dets)
        
        for det_id, amps in run_data.items():
            detector_data[det_id].append((run_id, amps))

    # --- Plotting Grid (4 Detectors x 4 Columns) ---
    fig, axes = plt.subplots(4, 4, figsize=(20, 16), sharex=True, sharey='row')
    plt.subplots_adjust(hspace=0.3, wspace=0.1)
    
    fig.suptitle("Landau Fits: Individual Middle Runs vs Combined (Physical Collimation)", fontsize=16)
    
    colors = ['royalblue', 'orange', 'green', 'crimson']
    
    for det_idx in range(4):
        det_id = det_idx + 1
        runs = detector_data[det_id]
        
        # Combined Data
        combined_amps = []
        for _, amps in runs:
            combined_amps.extend(amps)
            
        # Plot Individual Runs (Columns 0-2)
        for col in range(3):
            ax = axes[det_idx, col]
            if col < len(runs):
                run_id, amps = runs[col]
                ax.set_title(f"Det {det_id} @ {run_id}", fontsize=10)
                fit_and_plot(ax, amps, run_id, colors[det_idx])
            else:
                ax.axis('off') # Hide empty plot if < 3 runs
                
            if det_idx == 3: ax.set_xlabel("Amplitude (V)")
            if col == 0: ax.set_ylabel("Counts")
            ax.grid(True, alpha=0.3)

        # Plot Combined (Column 3)
        ax_comb = axes[det_idx, 3]
        ax_comb.set_title(f"Det {det_id} Combined", fontsize=10, fontweight='bold')
        fit_and_plot(ax_comb, combined_amps, "Combined", 'purple')
        ax_comb.grid(True, alpha=0.3)
        if det_idx == 3: ax_comb.set_xlabel("Amplitude (V)")

    out_path = os.path.join(RESULTS_DIR, "combined_landau_grid.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved grid plot to {out_path}")

if __name__ == "__main__":
    main()
