#!/usr/bin/env python3
"""
Calculate Calibration Constants
1. Re-analyze Simulation (v0200).
   - Method A: "Golden Events" (Strict Face-to-Face). Straight path, minimum dE.
   - Method B: "Realistic" (4-Fold Coincidence). Matches experimental trigger.
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
import os

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
    
    # ---------------------------------------------------------
    # Method A: Golden Events (Face-to-Face)
    # ---------------------------------------------------------
    print("\n[Method A] Golden Events (Strict Face-to-Face)")
    
    # Analyze Z coordinates to find faces
    scin0_in_z = df['Scin0_InZ']
    scin3_out_z = df['Scin3_OutZ']
    top_face_z = scin0_in_z.max()
    bottom_face_z = scin3_out_z.min()
    epsilon = 0.1 # mm
    
    # Filter
    mask_coinc = (
        (df['Edep_Scin0'] > THRESHOLD) & 
        (df['Edep_Scin1'] > THRESHOLD) & 
        (df['Edep_Scin2'] > THRESHOLD) & 
        (df['Edep_Scin3'] > THRESHOLD)
    )
    mask_geo = (
        (np.abs(df['Scin0_InZ'] - top_face_z) < epsilon) &
        (np.abs(df['Scin3_OutZ'] - bottom_face_z) < epsilon)
    )
    
    df_golden = df[mask_coinc & mask_geo]
    print(f"  Count: {len(df_golden)}")
    
    mpvs_golden = []
    for i in range(4):
        mpv, _ = fit_landau(df_golden[f'Edep_Scin{i}'], f"Scin{i}")
        if mpv: mpvs_golden.append(mpv)
    
    val_golden = np.mean(mpvs_golden) if mpvs_golden else 0
    print(f"  Average MPV (Golden): {val_golden:.2f} MeV")

    # ---------------------------------------------------------
    # Method B: Realistic (4-Fold Coincidence, Middle Detectors)
    # ---------------------------------------------------------
    print("\n[Method B] Realistic (4-Fold Coincidence)")
    
    df_real = df[mask_coinc]
    print(f"  Count: {len(df_real)}")
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Realistic Events (4-Fold Coinc) - Middle Detectors")
    
    mpvs_real = []
    # Only fit Middle Detectors (Scin1, Scin2) as they are the most stable
    # Scin0/Scin3 might have corner clipping effects in the simulation for angled tracks
    
    # Scin1
    mpv1, _ = fit_landau(df_real['Edep_Scin1'], "Scin1 (Mid1)", axes[0])
    axes[0].set_title(f"Scin1 MPV: {mpv1:.2f} MeV")
    if mpv1: mpvs_real.append(mpv1)
    
    # Scin2
    mpv2, _ = fit_landau(df_real['Edep_Scin2'], "Scin2 (Mid2)", axes[1])
    axes[1].set_title(f"Scin2 MPV: {mpv2:.2f} MeV")
    if mpv2: mpvs_real.append(mpv2)
    
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/calibration_fits_realistic.png")
    
    val_real = np.mean(mpvs_real) if mpvs_real else 0
    print(f"  Average MPV (Middle Detectors): {val_real:.2f} MeV")
    
    # ---------------------------------------------------------
    # Comparison & Decision
    # ---------------------------------------------------------
    print("\n--- Comparison ---")
    print(f"Golden (Vertical): {val_golden:.2f} MeV")
    print(f"Realistic (All):   {val_real:.2f} MeV")
    diff = (val_real - val_golden) / val_golden * 100
    print(f"Difference:        +{diff:.1f}% (Expected due to angled tracks)")
    
    true_energy = val_real
    print(f"\n>>> Selected True Energy: {true_energy:.2f} MeV (Realistic)")

    # ---------------------------------------------------------
    # Calibration Constants
    # ---------------------------------------------------------
    print("\n--- Calibration Constants ---")
    
    # Ch1 (Top): Run 003 Value
    calib_ch1 = true_energy / EXP_MPV_CH1
    print(f"Channel 1 (Top):    {EXP_MPV_CH1:.1f} mV -> {calib_ch1:.4f} MeV/mV")
    
    # Ch2 (Mid1): Run 002 Value
    calib_ch2 = true_energy / EXP_MPV_CH2
    print(f"Channel 2 (Mid1):   {EXP_MPV_CH2:.1f} mV -> {calib_ch2:.4f} MeV/mV")
    
    # Ch3 (Mid2): Run 002 Value
    calib_ch3 = true_energy / EXP_MPV_CH3
    print(f"Channel 3 (Mid2):   {EXP_MPV_CH3:.1f} mV -> {calib_ch3:.4f} MeV/mV")
    
    # Ch4 (Bottom): Run 003 Value
    calib_ch4 = true_energy / EXP_MPV_CH4
    print(f"Channel 4 (Bottom): {EXP_MPV_CH4:.1f} mV -> {calib_ch4:.4f} MeV/mV")

if __name__ == "__main__":
    main()
