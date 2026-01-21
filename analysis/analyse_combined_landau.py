#!/usr/bin/env python3
"""
Combined Landau Analysis (Runs 002-007)
Aggregates data from Middle detectors only to perform high-quality Landau fits.
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
RUN_PATTERN = "run00[2-7]*" # Matches run002 to run007
DEFAULT_CUT_THRESHOLD_MV = 50.0 
POSITIVE_NOISE_THRESHOLD = 0.03 # 30 mV
LANDAU_RANGE = (0.01, 0.4)
BINS = 60

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def parse_run_info(run_dir):
    dirname = os.path.basename(os.path.normpath(run_dir))
    match = re.search(r'config_(\d{4})', dirname)
    config_str = match.group(1) if match else "1234"
    return config_str

def get_middle_detectors(config_str):
    """
    Returns a list of detector IDs (integers) that are in the middle positions.
    config_str = "1234" -> Top=1, Mid1=2, Mid2=3, Bot=4. Returns [2, 3].
    """
    if len(config_str) != 4:
        return []
    return [int(config_str[1]), int(config_str[2])]

def load_run_data(run_dir, target_dets):
    """
    Loads data for specific detectors in a run.
    Returns a dictionary: {det_id: [amplitudes]}
    """
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files: return {}

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
        
    if not sets: return {}
    prefix = list(sets.keys())[0]
    file_map = sets[prefix]
    
    # Load all channels first to perform event filtering
    raw_data = {}
    num_events = 0
    
    for ch in range(1, 5):
        if ch not in file_map: return {}
        wfm = WfmReader(file_map[ch])
        _, v = wfm.read_data()
        raw_data[ch] = v
        if num_events == 0: num_events = wfm.num_frames
        else: num_events = min(num_events, wfm.num_frames)
        
    # Truncate
    for ch in raw_data:
        raw_data[ch] = raw_data[ch][:num_events]
        
    # Calculate Amplitudes
    amplitudes = {ch: np.abs(np.min(raw_data[ch], axis=1)) for ch in range(1, 5)}
    
    # Filter Events
    clean_amplitudes = {det: [] for det in target_dets}
    
    for i in range(num_events):
        # 1. Noise Check (Global)
        is_noise = False
        for ch in range(1, 5):
            if np.max(raw_data[ch][i]) > POSITIVE_NOISE_THRESHOLD:
                is_noise = True
                break
        if is_noise: continue
        
        # 2. No Amplitude Cut needed for Middle Detectors
        # They are physically collimated, so we keep the full distribution
        # to avoid truncating the real Landau tail.
        
        # 3. Store Data for Target Detectors (Ch N = Det N)
        for det_id in target_dets:
            clean_amplitudes[det_id].append(amplitudes[det_id][i])
            
    return clean_amplitudes

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    data_root = "data"
    run_dirs = sorted(glob.glob(os.path.join(data_root, RUN_PATTERN)))
    
    combined_data = {1: [], 2: [], 3: [], 4: []}
    
    print(f"Found {len(run_dirs)} runs matching {RUN_PATTERN}")
    
    for run_dir in run_dirs:
        config_str = parse_run_info(run_dir)
        mid_dets = get_middle_detectors(config_str)
        print(f"Processing {os.path.basename(run_dir)} (Config: {config_str}) -> Middle Dets: {mid_dets}")
        
        run_data = load_run_data(run_dir, mid_dets)
        
        for det_id, amps in run_data.items():
            combined_data[det_id].extend(amps)
            
            # Precise check for peak shift using Fit
            if len(amps) > 50:
                try:
                    y, x = np.histogram(amps, bins=40, range=LANDAU_RANGE)
                    bin_centers = (x[:-1] + x[1:]) / 2
                    peak_idx = np.argmax(y)
                    mpv_guess = bin_centers[peak_idx]
                    
                    popt, _ = curve_fit(landau_fit_func, bin_centers, y, 
                                        p0=[mpv_guess, 0.01, np.max(y)*0.01], 
                                        bounds=([0, 0, 0], [1, 1, np.inf]))
                    print(f"  - Det {det_id}: +{len(amps)} events | MPV: {popt[0]*1000:.2f} mV")
                except:
                    print(f"  - Det {det_id}: +{len(amps)} events | Fit Failed")
            else:
                print(f"  - Det {det_id}: +{len(amps)} events (Too few to fit)")

    print("\n--- Final Fits ---")
    # --- Plotting ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    fig.suptitle("Combined Landau Fits (Middle Detectors Only - Runs 002-007)\nPhysical Collimation (No Software Cuts, Noise Rejected)", fontsize=14)
    
    for i, det_id in enumerate(range(1, 5)):
        ax = axes[i]
        vals = np.array(combined_data[det_id])
        
        if len(vals) == 0:
            ax.text(0.5, 0.5, "No Data", ha='center', va='center')
            continue
            
        # Histogram
        y, x, _ = ax.hist(vals, bins=BINS, range=LANDAU_RANGE, 
                          density=False, histtype='stepfilled', alpha=0.4, label='Data', color=f'C{i}')
        
        bin_centers = (x[:-1] + x[1:]) / 2
        
        # Fit
        peak_idx = np.argmax(y)
        mpv_guess = bin_centers[peak_idx]
        try:
            popt, _ = curve_fit(landau_fit_func, bin_centers, y, 
                                p0=[mpv_guess, 0.01, np.max(y)*0.01], 
                                bounds=([0, 0, 0], [1, 1, np.inf]))
            
            mpv_val = popt[0]
            x_fine = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 200)
            ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=2, 
                    label=f'Fit\nMPV={mpv_val*1000:.1f} mV')
            print(f"Det {det_id} Combined MPV: {mpv_val*1000:.2f} mV")
        except Exception as e:
            print(f"Fit failed for Det {det_id}: {e}")
            
        ax.set_title(f"Detector {det_id} (N={len(vals)})")
        ax.set_xlabel("Amplitude (V)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(RESULTS_DIR, "combined_landau_fits.png")
    plt.savefig(out_path)
    print(f"Saved combined plot to {out_path}")

if __name__ == "__main__":
    main()
