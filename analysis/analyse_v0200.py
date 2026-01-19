#!/usr/bin/env python3
"""
Geant4 ROOT Analysis Tool for Cosmic Ray Muons (v0200 - 4 Detectors)
Author: Zichen Luo
Date: January 2026
Description: 
    Loads Geant4 ROOT output from v0200 simulation (4-detector stack).
    Filters for 4-fold coincidence events.
    Performs Landau (Moyal) fits on energy deposition data for all 4 detectors.
    Generates calibration plots and correlation checks.

Usage:
    python3 analysis/analyse_v0200.py
"""

import uproot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import moyal
from scipy.optimize import curve_fit
import argparse
import os
import sys

# ==========================================
# ANALYSIS CONFIGURATION
# ==========================================
DEFAULT_INPUT_FILE = "simulation/v0200_coincidence/build/DET01_Cosmic_Result.root"
OUTPUT_FILE = "results/v02_coincidence_calibration.png"
TREE_NAME = "CosmicData"
N_BINS = 100
LANDAU_RANGE = (10, 100) # Region for fitting (MeV)
FULL_RANGE = (0, 100)    # Region for global view (MeV)
THRESHOLD = 0.5          # MeV

def landau_fit_func(x, mpv, width, amp):
    """
    Wrapper for the Moyal PDF to allow amplitude scaling in curve_fit.
    """
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def perform_analysis(filepath, output_path):
    """
    Main analysis logic.
    """
    print(f"Loading: {filepath}...")
    
    # 1. Load Data
    try:
        with uproot.open(filepath) as file:
            if TREE_NAME not in file:
                print(f"Error: Tree '{TREE_NAME}' not found in {filepath}. Available keys: {file.keys()}")
                return False
            df = file[TREE_NAME].arrays(library="pd")
    except Exception as e:
        print(f"Error opening file: {e}")
        return False

    print(f"  - Total Events: {len(df)}")

    # 2. Filter 4-fold Coincidence
    # We require Energy Deposition > Threshold in ALL 4 scintillators
    coinc_mask = (
        (df['Edep_Scin0'] > THRESHOLD) & 
        (df['Edep_Scin1'] > THRESHOLD) & 
        (df['Edep_Scin2'] > THRESHOLD) & 
        (df['Edep_Scin3'] > THRESHOLD)
    )
    df_coinc = df[coinc_mask]
    
    rate = len(df_coinc) / len(df) if len(df) > 0 else 0
    print(f"  - 4-Fold Coincidence Events: {len(df_coinc)} ({rate:.1%})")

    if len(df_coinc) < 10:
        print("  - Warning: Too few coincidence events for fitting. Plotting raw histograms only.")
        # return False  <-- Disabled for testing on small files

    # 3. Setup Plotting Layout
    # 2x2 Grid for the 4 detectors + maybe a correlation plot?
    # Let's do a 3x2 layout.
    # [Scin0] [Scin1]
    # [Scin2] [Scin3]
    # [Correlation Top-Bot] [Global Trigger]
    
    fig = plt.figure(figsize=(15, 18), constrained_layout=True)
    gs = fig.add_gridspec(3, 2)
    
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])
    ax_corr = fig.add_subplot(gs[2, 0])
    ax_trig = fig.add_subplot(gs[2, 1])

    # --- Landau Fits ---
    mpv0 = fit_and_plot(ax0, df_coinc['Edep_Scin0'], "Scin0 (Top)", "royalblue")
    mpv1 = fit_and_plot(ax1, df_coinc['Edep_Scin1'], "Scin1", "orange")
    mpv2 = fit_and_plot(ax2, df_coinc['Edep_Scin2'], "Scin2", "green")
    mpv3 = fit_and_plot(ax3, df_coinc['Edep_Scin3'], "Scin3 (Bottom)", "crimson")

    # --- Correlation (Top vs Bottom) ---
    plot_correlation(ax_corr, df_coinc, 'Edep_Scin0', 'Edep_Scin3', "Top (Scin0) vs Bottom (Scin3)")

    # --- Trigger Check ---
    plot_trigger_check(ax_trig, df, df_coinc)

    # 4. Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"  - Plot saved to: {output_path}")
    
    return True

def fit_and_plot(axis, data, label, color):
    """Fits Moyal distribution and plots on the given axis."""
    # Filter to fit range
    data_in_range = data[(data >= LANDAU_RANGE[0]) & (data <= LANDAU_RANGE[1])]
    
    if len(data_in_range) == 0:
        axis.text(0.5, 0.5, "No Data", ha='center', va='center')
        return 0.0

    # Histogram
    y_data, bin_edges, _ = axis.hist(data_in_range, bins=N_BINS, range=LANDAU_RANGE,
                                     histtype='stepfilled', alpha=0.4, color=color, label='Data')
    
    # Calculate fit x/y
    x_data = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Initial Guesses
    guess_mpv = x_data[np.argmax(y_data)]
    guess_width = 5.0
    guess_amp = np.max(y_data) * 5.0
    
    mpv_fit = 0.0
    try:
        popt, _ = curve_fit(landau_fit_func, x_data, y_data, p0=[guess_mpv, guess_width, guess_amp])
        mpv_fit, width_fit, amp_fit = popt
        
        # Plot Curve
        x_curve = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 200)
        y_curve = landau_fit_func(x_curve, *popt)
        axis.plot(x_curve, y_curve, color='black', linestyle='--', linewidth=1.5, label=f'Fit (MPV={mpv_fit:.1f})')
    except:
        print(f"Fit failed for {label}")

    axis.set_title(f"{label} Energy Deposition")
    axis.set_xlabel("Energy (MeV)")
    axis.set_ylabel("Counts")
    axis.legend()
    axis.grid(True, alpha=0.3)
    return mpv_fit

def plot_correlation(axis, df, col1, col2, title):
    """Scatter plot."""
    axis.scatter(df[col1], df[col2], c='purple', alpha=0.2, s=10)
    axis.set_title(title)
    axis.set_xlabel(f"{col1} (MeV)")
    axis.set_ylabel(f"{col2} (MeV)")
    axis.set_xlim(LANDAU_RANGE)
    axis.set_ylim(LANDAU_RANGE)
    axis.grid(True, linestyle='--', alpha=0.5)

def plot_trigger_check(axis, df, df_coinc):
    """Compare raw vs coincidence events for Top Scintillator."""
    axis.hist(df['Edep_Scin0'], bins=N_BINS, range=FULL_RANGE, 
              histtype='stepfilled', alpha=0.2, color='gray', label='All Events (Scin0)')
    
    axis.hist(df_coinc['Edep_Scin0'], bins=N_BINS, range=FULL_RANGE, 
              histtype='step', linewidth=1.5, color='blue', label='Coincidence (Scin0)')
    
    axis.set_title("Trigger Efficiency Check (Scin0)")
    axis.set_xlabel("Energy (MeV)")
    axis.set_yscale('log')
    axis.legend(loc='upper right', fontsize='small')
    axis.grid(True, alpha=0.3)

def main():
    parser = argparse.ArgumentParser(description="Analyse Geant4 ROOT Cosmic Data (v0200).")
    parser.add_argument("file", nargs='?', default=DEFAULT_INPUT_FILE, help="Path to the ROOT file.")
    parser.add_argument("--output", "-o", default=OUTPUT_FILE, help="Path to save the output plot.")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        print(f"Usage: python3 analysis/analyse_v0200.py [path_to_root_file]")
        return
            
    success = perform_analysis(args.file, args.output)
    if not success:
        print("Analysis failed.")

if __name__ == "__main__":
    main()
