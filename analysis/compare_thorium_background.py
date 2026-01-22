#!/usr/bin/env python3
"""
Thorium vs Background Comparison (Run 007 vs Run 008)
Compares energy deposition spectra to identify the effect of the Thorium source.
Applies final calibration constants to convert mV to MeV.
"""

import numpy as np
import matplotlib.pyplot as plt
from wfm_reader import WfmReader
import os
import glob

# --- Configuration ---
RESULTS_DIR = "results/physical"
RUN7_DIR = "data/run007_1000_config_1342"
RUN8_DIR = "data/run008_1000_config_1342_thorium"

# Calibration Constants (MeV/mV) from Final Analysis
CALIBRATION = {
    1: 0.1083,
    2: 0.1166,
    3: 0.1135,
    4: 0.1002
}

DETECTOR_LABELS = {
    1: "Det 1 (Top)",
    2: "Det 2 (Bot)",
    3: "Det 3 (Mid1)",
    4: "Det 4 (Mid2)"
}

def load_amplitudes(run_dir):
    """
    Loads WFM data and returns a dictionary of amplitudes {ch: [volts]}
    """
    if not os.path.exists(run_dir):
        print(f"Warning: Directory not found: {run_dir}")
        return {}

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
    
    amplitudes = {}
    
    for ch in range(1, 5):
        if ch not in file_map: continue
        wfm = WfmReader(file_map[ch])
        _, v = wfm.read_data()
        
        # Calculate Peak Amplitude (Negative polarity -> take min and abs)
        amps = np.abs(np.min(v, axis=1))
        amplitudes[ch] = amps
        
    return amplitudes

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print(f"Loading Run 007 (Background)...")
    data_bg = load_amplitudes(RUN7_DIR)
    
    print(f"Loading Run 008 (Thorium)...")
    data_th = load_amplitudes(RUN8_DIR)
    
    if not data_bg or not data_th:
        print("Error: Could not load data for comparison.")
        return

    # --- Plotting ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    fig.suptitle("Thorium Source vs Cosmic Background\n(Run 008 vs Run 007 - Stack 1342)", fontsize=16)
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes[i]
        
        # Convert to MeV
        bg_mev = data_bg[ch] * 1000 * CALIBRATION[ch]
        th_mev = data_th[ch] * 1000 * CALIBRATION[ch]
        
        # Plot Histograms
        # Range: 0 to 60 MeV covers the Landau peak (~30 MeV) and low energy
        bins = np.linspace(0, 60, 61) 
        
        # Plot Background
        ax.hist(bg_mev, bins=bins, histtype='step', linewidth=2, 
                color='royalblue', label=f'Background (N={len(bg_mev)})', density=True)
        
        # Plot Thorium
        ax.hist(th_mev, bins=bins, histtype='stepfilled', alpha=0.3, 
                color='crimson', label=f'Thorium (N={len(th_mev)})', density=True)
        ax.hist(th_mev, bins=bins, histtype='step', linewidth=2, 
                color='crimson', density=True)
        
        ax.set_title(DETECTOR_LABELS[ch])
        ax.set_xlabel("Energy Deposited (MeV)")
        ax.set_ylabel("Normalized Count Density")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add inset for low energy region if relevant? 
        # For now, let's stick to the main view to see if there's a gross shift.

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(RESULTS_DIR, "thorium_comparison.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved comparison plot to {out_path}")

if __name__ == "__main__":
    main()
