#!/usr/bin/env python3
"""
Calculate Calibration Constants
1. Re-analyze Simulation (v0200) with Geometric Filtering (Golden Events).
2. Calculate True Energy Deposition (MPV).
3. Combine with Experimental MPVs to get Calibration Constants (MeV/mV).
"""

import uproot
import numpy as np
import pandas as pd
from scipy.stats import moyal
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys

# Configuration
ROOT_FILE = "simulation/v0200_coincidence/build/DET01_Cosmic_Result.root"
TREE_NAME = "CosmicData"
LANDAU_RANGE = (10, 50) # MeV
THRESHOLD = 0.5 # MeV

# Experimental MPVs (mV)
# Run 003 (Switched): Ch1, Ch4 are valid
EXP_MPV_CH1 = 272.5
EXP_MPV_CH4 = 293.8
# Run 002 (Unswitched): Ch2, Ch3 are valid
EXP_MPV_CH2 = 258.6
EXP_MPV_CH3 = 264.1

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def fit_landau(data, label, ax=None):
    data_in_range = data[(data >= LANDAU_RANGE[0]) & (data <= LANDAU_RANGE[1])]
    
    if len(data_in_range) < 50:
        return None, None
    
    y, bin_edges = np.histogram(data_in_range, bins=50, range=LANDAU_RANGE)
    x = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    guess_mpv = x[np.argmax(y)]
    guess_width = 2.0
    guess_amp = np.max(y) * 2.0
    
    try:
        popt, _ = curve_fit(landau_fit_func, x, y, p0=[guess_mpv, guess_width, guess_amp])
        mpv, width, amp = popt
        
        if ax:
            ax.hist(data_in_range, bins=50, range=LANDAU_RANGE, histtype='stepfilled', alpha=0.4, label=f"{label} Data")
            x_curve = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 200)
            ax.plot(x_curve, landau_fit_func(x_curve, *popt), 'r-', label=f'Fit MPV={mpv:.2f}')
            ax.legend()
            
        return mpv, width
    except:
        return None, None

def main():
    print("--- Calibration Calculation ---")
    
    # 1. Load Simulation Data
    try:
        with uproot.open(ROOT_FILE) as file:
            df = file[TREE_NAME].arrays(library="pd")
    except Exception as e:
        print(f"Error loading ROOT file: {e}")
        return

    print(f"Total Simulated Events: {len(df)}")
    
    # 2. Geometric Filtering (Golden Events)
    # Identify Top and Bottom Faces
    # Top Detector: Scin0. We want Entry via Top Face.
    # Bottom Detector: Scin3. We want Exit via Bottom Face.
    
    # Analyze Z coordinates to find faces
    scin0_in_z = df['Scin0_InZ']
    scin3_out_z = df['Scin3_OutZ']
    
    top_face_z = scin0_in_z.max()
    bottom_face_z = scin3_out_z.min()
    
    print(f"Geometry Detected: Top Z ~ {top_face_z:.2f}, Bottom Z ~ {bottom_face_z:.2f}")
    
    # Define epsilon for "on the face"
    epsilon = 0.1 # mm
    
    # Filter
    # 1. 4-fold Coincidence
    mask_coinc = (
        (df['Edep_Scin0'] > THRESHOLD) & 
        (df['Edep_Scin1'] > THRESHOLD) & 
        (df['Edep_Scin2'] > THRESHOLD) & 
        (df['Edep_Scin3'] > THRESHOLD)
    )
    
    # 2. Geometric (Through Top and Bottom Faces)
    mask_geo = (
        (np.abs(df['Scin0_InZ'] - top_face_z) < epsilon) &
        (np.abs(df['Scin3_OutZ'] - bottom_face_z) < epsilon)
    )
    
    df_golden = df[mask_coinc & mask_geo]
    print(f"Golden Events (Face-to-Face & Coincidence): {len(df_golden)}")
    
    # 3. Fit Landau for Golden Events
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()
    fig.suptitle("Golden Events Energy Deposition (Simulated)")
    
    mpvs = {}
    for i in range(4):
        col = f'Edep_Scin{i}'
        mpv, width = fit_landau(df_golden[col], f"Scin{i}", axes[i])
        if mpv:
            mpvs[i] = mpv
            print(f"Scin{i} MPV: {mpv:.2f} MeV")
        else:
            print(f"Scin{i} Fit Failed")
            
    plt.tight_layout()
    plt.savefig("results/golden_events_fits.png")
    
    # 4. Calculate True Energy
    # User Suggestion: "should we choose the average instead as the true value?"
    # With Golden Events (Straight through), all detectors should see similar path lengths (~thickness).
    # So averaging is valid.
    
    valid_mpvs = [v for v in mpvs.values()]
    if valid_mpvs:
        true_energy = np.mean(valid_mpvs)
        print(f"\nAverage True Energy (from Golden Events): {true_energy:.2f} MeV")
    else:
        print("Could not determine True Energy.")
        return

    # 5. Calculate Calibration Constants
    print("\n--- Calibration Constants ---")
    
    # Mapping: Scin0->Ch1, Scin1->Ch2, Scin2->Ch3, Scin3->Ch4 (Standard Stack)
    # Ch1 (Top): Run 003 Value
    calib_ch1 = true_energy / EXP_MPV_CH1
    print(f"Channel 1 (Top):    {EXP_MPV_CH1:.1f} mV -> {calib_ch1:.4f} MeV/mV")
    
    # Ch2 (Mid1): Run 002 Value
    calib_ch2 = true_energy / EXP_MPV_CH2
    print(f"Channel 2 (Mid1):   {EXP_MPV_CH2:.1f} mV -> {calib_ch2:.4f} MeV/mV")
    
    # Ch3 (Mid2): Run 002 Value
    calib_ch3 = true_energy / EXP_MPV_CH3
    print(f"Channel 3 (Mid2):   {EXP_MPV_CH3:.1f} mV -> {calib_ch3:.4f} MeV/mV")
    
    # Ch4 (Bot): Run 003 Value
    calib_ch4 = true_energy / EXP_MPV_CH4
    print(f"Channel 4 (Bottom): {EXP_MPV_CH4:.1f} mV -> {calib_ch4:.4f} MeV/mV")

if __name__ == "__main__":
    main()
