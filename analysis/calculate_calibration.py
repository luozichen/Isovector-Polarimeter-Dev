#!/usr/bin/env python3
"""
Calculate Energy Calibration Constants
1. Loads 1M event Geant4 simulation data (v0200).
2. Selects 4-fold coincidence events.
3. Fits Landau to Middle Detectors (Scin1, Scin2) to get Reference Energy (MeV).
   (Middle detectors are used to minimize geometric clipping effects, matching experimental "Golden" logic).
4. Uses experimental MPVs (from Combined Landau Analysis) to calculate calibration constants (MeV/mV).
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import moyal
import os

# --- Configuration ---
ROOT_FILE = "simulation/v0200_coincidence/build/DET01_Cosmic_Result_long.root"
TREE_NAME = "CosmicData"
THRESHOLD_MEV = 0.5
FIT_RANGE_MEV = (10, 60)
BINS = 100

# Experimental MPVs (from combined_landau_grid.png analysis) - in mV
EXP_MPV_MV = {
    1: 277.16,
    2: 257.40,
    3: 264.44,
    4: 299.42
}

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def get_simulation_mpv(df, scint_name):
    """
    Fits Landau to the energy deposition of a specific scintillator in the dataframe.
    """
    data = df[scint_name]
    
    # Histogram
    counts, bin_edges = np.histogram(data, bins=BINS, range=FIT_RANGE_MEV)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Guess parameters
    peak_idx = np.argmax(counts)
    mpv_guess = bin_centers[peak_idx]
    
    try:
        popt, _ = curve_fit(landau_fit_func, bin_centers, counts, 
                            p0=[mpv_guess, 2.0, np.max(counts)*5],
                            bounds=([0, 0, 0], [100, 20, np.inf]))
        return popt[0] # MPV
    except Exception as e:
        print(f"Fit failed for {scint_name}: {e}")
        return None

def main():
    print(f"Loading simulation: {ROOT_FILE}")
    if not os.path.exists(ROOT_FILE):
        print("Error: ROOT file not found.")
        return

    with uproot.open(ROOT_FILE) as file:
        df = file[TREE_NAME].arrays(library="pd")

    print(f"Total Simulated Events: {len(df)}")

    # 4-Fold Coincidence Filter
    mask = (
        (df['Edep_Scin0'] > THRESHOLD_MEV) & 
        (df['Edep_Scin1'] > THRESHOLD_MEV) & 
        (df['Edep_Scin2'] > THRESHOLD_MEV) & 
        (df['Edep_Scin3'] > THRESHOLD_MEV)
    )
    df_coinc = df[mask]
    print(f"4-Fold Coincidence Events: {len(df_coinc)}")

    # Get Simulation MPVs for Middle Detectors
    mpv_scin1 = get_simulation_mpv(df_coinc, 'Edep_Scin1')
    mpv_scin2 = get_simulation_mpv(df_coinc, 'Edep_Scin2')
    
    if mpv_scin1 is None or mpv_scin2 is None:
        print("Error: Could not fit simulation data.")
        return

    print("-" * 40)
    print(f"Simulation MPV (Scin1 - Mid1): {mpv_scin1:.4f} MeV")
    print(f"Simulation MPV (Scin2 - Mid2): {mpv_scin2:.4f} MeV")
    
    # Reference Energy is the average of the middle detectors
    # This represents the "True" expected energy deposition for a detector 
    # in the middle of the stack with 4-fold coincidence logic.
    ref_energy_mev = (mpv_scin1 + mpv_scin2) / 2
    print(f"Reference Energy (Avg Mid):   {ref_energy_mev:.4f} MeV")
    print("-" * 40)

    print("Calibration Constants (MeV/mV):")
    print(f"{'Det':<4} | {'Exp MPV (mV)':<12} | {'Calib (MeV/mV)':<15} | {'1 MeV in mV':<12}")
    print("-" * 50)
    
    results = []
    for det_id in range(1, 5):
        exp_mv = EXP_MPV_MV[det_id]
        calib_const = ref_energy_mev / exp_mv
        mv_per_mev = 1.0 / calib_const
        
        print(f"{det_id:<4} | {exp_mv:<12.2f} | {calib_const:<15.6f} | {mv_per_mev:<12.2f}")
        results.append((det_id, calib_const))

if __name__ == "__main__":
    main()