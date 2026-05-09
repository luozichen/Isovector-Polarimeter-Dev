#!/usr/bin/env python3
"""
Thesis Defense Plot: Simulation Results (1M Run)
Produces a beautiful 1x4 horizontal grid of simulation energy deposition (Landau).
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

from analysis import config

# Simulation configuration
INPUT_FILE = "simulation/v0200_coincidence/build/DET01_Cosmic_Result_long.root"
TREE_NAME = "CosmicData"
THRESHOLD = 0.5 # MeV
LANDAU_RANGE = (10, 80) # Region for fitting (MeV)
N_BINS = 100

DETECTOR_COLORS = {
    0: '#E57373', # Scin0 (Red)
    1: '#64B5F6', # Scin1 (Blue)
    2: '#81C784', # Scin2 (Green)
    3: '#FFB74D', # Scin3 (Orange)
}

def landau_fit_func(x, mpv, width, amp):
    return amp * moyal.pdf(x, loc=mpv, scale=width)

def main():
    root_path = os.path.join(PROJECT_ROOT, INPUT_FILE)
    if not os.path.exists(root_path):
        print(f"Error: {root_path} not found")
        # Trying relative path if absolute fails
        root_path = INPUT_FILE
        if not os.path.exists(root_path):
            return

    print(f"Loading simulation data: {root_path}")
    try:
        with uproot.open(root_path) as file:
            df = file[TREE_NAME].arrays(library="pd")
    except Exception as e:
        print(f"Error opening ROOT file: {e}")
        return

    # Coincidence filtering
    coinc_mask = (df['Edep_Scin0'] > THRESHOLD) & (df['Edep_Scin1'] > THRESHOLD) & \
                 (df['Edep_Scin2'] > THRESHOLD) & (df['Edep_Scin3'] > THRESHOLD)
    df_coinc = df[coinc_mask]
    print(f"  - Total events in coincidence: {len(df_coinc)}")

    # 2. Thesis Plotting Properties
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

    # Create 1x4 horizontal plot
    fig, axes = plt.subplots(1, 4, figsize=(22, 5))
    
    for i in range(4):
        ax = axes[i]
        scin_name = f'Edep_Scin{i}'
        data = df_coinc[scin_name]
        color = DETECTOR_COLORS[i]
        
        # Draw nice histogram
        y, x, _ = ax.hist(data, bins=N_BINS, range=LANDAU_RANGE,
                          density=False, histtype='stepfilled', alpha=0.7, 
                          color=color, edgecolor='black', linewidth=0.5)
        bin_centers = (x[:-1] + x[1:]) / 2
        
        peak_idx = np.argmax(y)
        guess_mpv = bin_centers[peak_idx]
        guess_width = 3.0 # In MeV
        guess_amp = np.max(y) * 5.0
        
        try:
            popt, _ = curve_fit(landau_fit_func, bin_centers, y, 
                                p0=[guess_mpv, guess_width, guess_amp], 
                                maxfev=10000)
            mpv_fit = popt[0]
            
            # Plot Fit Line
            x_fine = np.linspace(LANDAU_RANGE[0], LANDAU_RANGE[1], 300)
            ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=2.5)
            
            # Dynamic zooming: Focus on the peak
            nonzero_idx = np.where(y > np.max(y) * 0.02)[0]
            if len(nonzero_idx) > 0:
                start_x = x[nonzero_idx[0]]
                end_x = x[nonzero_idx[-1] + 1]
                padding = (end_x - start_x) * 0.15 
                ax.set_xlim(max(0, start_x - padding), min(LANDAU_RANGE[1], end_x + padding))
            
            # Subtitle or simple title
            scin_pos = ["Top", "Mid-1", "Mid-2", "Bottom"][i]
            ax.set_title(f"Detector {i+1} ({scin_pos})", fontweight='bold', pad=15)
            
            # MPV Text Box
            textstr = f"MPV: {mpv_fit:.2f} MeV\nN = {len(data)}"
            props = dict(boxstyle='round,pad=0.6', facecolor='white', alpha=0.95, edgecolor='#BDBDBD')
            ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=16,
                    verticalalignment='top', horizontalalignment='right', bbox=props)
                    
        except Exception as e:
            print(f"Fit failed for Det {i+1}: {e}")
            ax.set_title(f"Detector {i+1} (Fit failed)")

        # Styling
        ax.set_xlabel("Energy Deposition (MeV)", labelpad=8)
        if i == 0:
            ax.set_ylabel("Counts / bin", labelpad=8)
            
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
        ax.grid(True, alpha=0.25, linestyle='-', linewidth=1.5)

    plt.tight_layout()
    
    # Save high-res
    output_path = os.path.join(PROJECT_ROOT, "results/simulation/thesis_sim_landau.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved high-res thesis simulation plot: {output_path}")

if __name__ == "__main__":
    main()
