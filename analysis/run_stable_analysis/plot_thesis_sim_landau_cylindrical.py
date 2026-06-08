#!/usr/bin/env python3
"""
Thesis Defense Plot: Cylindrical Simulation Results (10M Run)
Produces a beautiful 1x2 horizontal grid of simulation energy deposition (Landau).
Matches the style of Chapter 5's cuboid simulation plots.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import moyal
from scipy.optimize import curve_fit
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

# Simulation configuration
INPUT_FILE_PRIMARY = "simulation/v0600_cylindrical_coincidence/build/output/DET01_Cosmic_Result_long.root"
INPUT_FILE_FALLBACK = "simulation/v0600_cylindrical_coincidence/build/DET01_Cosmic_Result_long.root"
TREE_NAME = "CosmicData"
LANDAU_RANGE = (0.5, 4.5) # Region for plotting (MeV)
N_BINS = 100

DETECTOR_COLORS = {
    0: '#64B5F6', # Top (Blue)
    1: '#E57373', # Bottom (Red)
}

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def main():
    root_path = os.path.join(PROJECT_ROOT, INPUT_FILE_PRIMARY)
    if not os.path.exists(root_path):
        root_path = os.path.join(PROJECT_ROOT, INPUT_FILE_FALLBACK)
        if not os.path.exists(root_path):
            print("Error: ROOT file not found.")
            return

    print(f"Loading simulation data: {root_path}")
    try:
        with uproot.open(root_path) as file:
            df = file[TREE_NAME].arrays(["Edep_Scin0", "Edep_Scin1", "PE_PMT0", "PE_PMT1"], library="pd")
    except Exception as e:
        print(f"Error opening ROOT file: {e}")
        return

    # Coincidence filtering
    coinc_mask = (df['PE_PMT0'] > 50) & (df['PE_PMT1'] > 50)
    df_coinc = df[coinc_mask]
    print(f"  - Total events in coincidence: {len(df_coinc)}")

    # Thesis Plotting Properties
    plt.rcParams.update({
        'font.size': 14,
        'font.weight': 'bold',
        'axes.titlesize': 22,
        'axes.labelsize': 20,
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 12,
    })

    # Create 1x2 horizontal plot
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    
    mpvs = []
    
    for i in range(2):
        ax = axes[i]
        scin_name = f'Edep_Scin{i}'
        data = df_coinc[scin_name]
        color = DETECTOR_COLORS[i]
        
        # Draw nice histogram
        y, x, _ = ax.hist(data, bins=N_BINS, range=(0, 5),
                          density=False, histtype='stepfilled', alpha=0.7, 
                          color=color, edgecolor='black', linewidth=0.5)
        bin_centers = (x[:-1] + x[1:]) / 2
        
        peak_idx = np.argmax(y)
        peak_pos = bin_centers[peak_idx]
        
        # Fit range strictly on peak_pos * 0.5 to peak_pos * 2.0 (ROOT range)
        fit_mask = (bin_centers >= peak_pos * 0.5) & (bin_centers <= peak_pos * 2.0)
        fit_x = bin_centers[fit_mask]
        fit_y = y[fit_mask]
        
        guess_mpv = peak_pos
        guess_width = 0.12
        guess_amp = np.max(y) * 1.5
        
        try:
            popt, _ = curve_fit(landau_fit_func, fit_x, fit_y, 
                                p0=[guess_mpv, guess_width, guess_amp], 
                                maxfev=10000)
            mpv_fit = popt[0]
            mpvs.append(mpv_fit)
            
            # Plot Fit Line
            x_fine = np.linspace(0.2, 4.8, 300)
            ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=2.5)
            
            # Subtitle or simple title
            scin_pos = ["Top", "Bottom"][i]
            ax.set_title(f"Detector {i} ({scin_pos})", fontweight='bold', pad=15)
            
            # MPV Text Box
            textstr = f"MPV: {mpv_fit:.2f} MeV\nN = {len(data)}"
            props = dict(boxstyle='round,pad=0.6', facecolor='white', alpha=0.95, edgecolor='#BDBDBD')
            ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=16,
                    verticalalignment='top', horizontalalignment='right', bbox=props)
                    
        except Exception as e:
            print(f"Fit failed for Det {i}: {e}")
            ax.set_title(f"Detector {i} (Fit failed)")

        # Styling
        ax.set_xlabel("Energy Deposition (MeV)", labelpad=8)
        if i == 0:
            ax.set_ylabel("Counts / bin", labelpad=8)
            
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
        ax.grid(True, alpha=0.25, linestyle='-', linewidth=1.5)
        ax.set_xlim(0.2, 4.8)

    plt.tight_layout()
    
    # Save high-res
    output_path = os.path.join(PROJECT_ROOT, "results/simulation/v0600_landau_fits.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved high-res cylindrical simulation plot: {output_path}")
    if len(mpvs) == 2:
        print(f"Average MPV: {np.mean(mpvs):.4f} MeV")

if __name__ == "__main__":
    main()
