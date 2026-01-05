#!/usr/bin/env python3
"""
Geant4 ROOT Analysis Tool for Cosmic Ray Muons
Author: Zichen Luo
Date: January 2026
Description: 
    Loads Geant4 ROOT output, filters for coincidence events, 
    and performs Landau (Moyal) fits on energy deposition data.
    Generates calibration plots and correlation checks.

Usage:
    ./analyse_root.py data.root
    ./analyse_root.py data.root -o results/plot.png
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
DEFAULT_TREE_NAME = "CosmicData"
N_BINS = 100
LANDAU_RANGE = (10, 100) # Region for fitting (MeV)
FULL_RANGE = (0, 100)    # Region for global view (MeV)
DEFAULT_THRESHOLD = 0.5  # MeV

def landau_fit_func(x, mpv, width, amp):
    """
    Wrapper for the Moyal PDF to allow amplitude scaling in curve_fit.
    """
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def perform_analysis(filepath, args):
    """
    Main analysis logic for a single file.
    """
    print(f"Loading: {filepath}...")
    
    # 1. Load Data
    try:
        with uproot.open(filepath) as file:
            if args.tree not in file:
                print(f"Error: Tree '{args.tree}' not found in {filepath}. Available keys: {file.keys()}")
                return False
            df = file[args.tree].arrays(library="pd")
    except Exception as e:
        print(f"Error opening file: {e}")
        return False

    print(f"  - Total Events: {len(df)}")

    # 2. Filter Coincidence
    coincidence_mask = (df['Edep_Scin0'] > args.threshold) & (df['Edep_Scin1'] > args.threshold)
    df_coinc = df[coincidence_mask]
    
    rate = len(df_coinc) / len(df) if len(df) > 0 else 0
    print(f"  - Coincidence Events: {len(df_coinc)} ({rate:.1%})")

    if len(df_coinc) < 10:
        print("  - Warning: Too few coincidence events for fitting.")
        return False

    # 3. Setup Plotting Layout (3 Subplots)
    fig = plt.figure(figsize=(18, 6), constrained_layout=True)
    gs = fig.add_gridspec(1, 3)
    
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])

    # --- PLOT 1: Raw Data (Log Scale) ---
    plot_overlay(ax1, df, df_coinc)

    # --- PLOT 2: Landau Fit (Coincidence Only) ---
    mpv0 = fit_and_plot(ax2, df_coinc['Edep_Scin0'], "Scin0 (Top)", "royalblue")
    mpv1 = fit_and_plot(ax2, df_coinc['Edep_Scin1'], "Scin1 (Bottom)", "crimson", add_new_plot=False)
    ax2.set_title(f"Physics Run: Landau Fit\nMPV Top: {mpv0:.1f} MeV | MPV Bot: {mpv1:.1f} MeV")
    ax2.legend()

    # --- PLOT 3: Correlation ---
    plot_correlation(ax3, df_coinc)

    # 4. Save or Show
    if args.output:
        plt.savefig(args.output, dpi=150)
        print(f"  - Plot saved to: {args.output}")
    else:
        plt.show()
    
    return True

def plot_overlay(axis, df, df_coinc):
    """Plots raw data vs coincidence data on log scale."""
    axis.hist(df['Edep_Scin0'], bins=N_BINS, range=FULL_RANGE, 
              histtype='stepfilled', alpha=0.2, color='gray', label='All Events')
    
    axis.hist(df_coinc['Edep_Scin0'], bins=N_BINS, range=FULL_RANGE, 
              histtype='step', linewidth=1.5, color='blue', label='Top (Coinc)')
    axis.hist(df_coinc['Edep_Scin1'], bins=N_BINS, range=FULL_RANGE, 
              histtype='step', linewidth=1.5, color='red', label='Bot (Coinc)')
    
    axis.set_title("Trigger Logic Check (Log Scale)")
    axis.set_xlabel("Energy (MeV)")
    axis.set_yscale('log')
    axis.legend(loc='upper right', fontsize='small')
    axis.grid(True, alpha=0.3)

def fit_and_plot(axis, data, label, color, add_new_plot=True):
    """Fits Moyal distribution and plots on the given axis."""
    # Filter to fit range
    data_in_range = data[(data >= LANDAU_RANGE[0]) & (data <= LANDAU_RANGE[1])]
    
    # Histogram
    y_data, bin_edges, _ = axis.hist(data_in_range, bins=N_BINS, range=LANDAU_RANGE,
                                     histtype='stepfilled', alpha=0.4, color=color, label=label)
    
    # Calculate fit x/y
    x_data = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Initial Guesses
    guess_mpv = x_data[np.argmax(y_data)]
    guess_width = 5.0
    guess_amp = np.max(y_data) * 5.0
    
    try:
        popt, _ = curve_fit(landau_fit_func, x_data, y_data, p0=[guess_mpv, guess_width, guess_amp])
        mpv_fit, width_fit, amp_fit = popt
        
        # Plot Curve
        x_curve = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 200)
        y_curve = landau_fit_func(x_curve, *popt)
        axis.plot(x_curve, y_curve, color=color, linestyle='-', linewidth=2)
        return mpv_fit
    except:
        print(f"Fit failed for {label}")
        return 0.0

def plot_correlation(axis, df_coinc):
    """Scatter plot for top vs bottom."""
    axis.scatter(df_coinc['Edep_Scin0'], df_coinc['Edep_Scin1'], 
                 c='purple', alpha=0.2, s=10, label='Events')
    
    axis.set_title("Correlation & Clipping Check")
    axis.set_xlabel("Top Detector (MeV)")
    axis.set_ylabel("Bottom Detector (MeV)")
    axis.set_xlim(LANDAU_RANGE)
    axis.set_ylim(LANDAU_RANGE)
    axis.grid(True, linestyle='--', alpha=0.5)
    
    # Annotation for Clipping
    axis.annotate('Corner Clipping?', xy=(30, 20), xytext=(50, 15),
                  arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                  fontsize='small')

def main():
    parser = argparse.ArgumentParser(description="Analyse Geant4 ROOT Cosmic Data.")
    parser.add_argument("files", nargs='+', help="ROOT files to analyse.")
    parser.add_argument("--tree", default=DEFAULT_TREE_NAME, help="Name of the TTree.")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Coincidence threshold (MeV).")
    parser.add_argument("--output", "-o", help="Save plot to file (e.g., results/plot.png).")
    
    args = parser.parse_args()

    for filepath in args.files:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        success = perform_analysis(filepath, args)
        if not success:
            print("Analysis failed.")

if __name__ == "__main__":
    main()
