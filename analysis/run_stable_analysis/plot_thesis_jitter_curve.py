#!/usr/bin/env python3
"""
Thesis Defense Plot: Intrinsic Jitter comparison curve.
Produces a single beautiful pane showing jitter (sigma) vs Voltage for all 4 detectors.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from analysis import config

DETECTOR_COLORS = {
    1: '#E57373', # Red
    2: '#64B5F6', # Blue
    3: '#81C784', # Green
    4: '#FFB74D', # Orange
}

# Values extracted from voltage_comparison_summary_corrected.txt
VOLTAGES = [800, 850, 900]
NEW_JITTER = {
    1: [0.5660, 0.4482, 0.4972],
    2: [0.5375, 0.5448, 0.4952],
    3: [0.6555, 0.6454, 0.5821],
    4: [0.4735, 0.5140, 0.4932]
}

# Previous 800V baseline for context
OLD_JITTER = {
    1: 0.5050,
    2: 0.5070,
    3: 0.5410,
    4: 0.5310
}

RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results_corrected")

def main():
    os.makedirs(RESULTS_BASE, exist_ok=True)
    
    # 1. Thesis Plotting Properties
    plt.rcParams.update({
        'font.size': 14,
        'font.weight': 'bold',
        'axes.titlesize': 22,
        'axes.labelsize': 20,
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 13,
    })
    
    # Create larger panel (slide-filling layout, slightly squeezed horizontally)
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Plot New Jitter Data
    for det_id in range(1, 5):
        ax.plot(VOLTAGES, NEW_JITTER[det_id], 'o-', color=DETECTOR_COLORS[det_id],
                markersize=12, linewidth=3.5, label=f"Det {det_id} (New PCB)")
        
        # Overlay Old 800V Baseline point as a square
        ax.plot(800, OLD_JITTER[det_id], 's', color=DETECTOR_COLORS[det_id], markersize=14,
                markeredgecolor='black', markeredgewidth=2.0, alpha=0.45)
    
    # Add a custom legend entry for old markers
    ax.plot([], [], 's', color='gray', markersize=12,
             markeredgecolor='black', markeredgewidth=2.0, alpha=0.45,
             label='Old Baseline (v2.2 @ 800V)')
    
    # Axis configuration
    ax.set_title("Intrinsic Jitter (σ) vs Working Voltage", pad=20)
    ax.set_xlabel("HV Operating Voltage (V)", labelpad=12)
    ax.set_ylabel("Timing Resolution σ (ns)", labelpad=12)
    
    # Spines/Border Aesthetics
    for spine in ax.spines.values():
        spine.set_linewidth(2.5)
        
    ax.grid(True, alpha=0.25, linestyle='-', linewidth=1.5)
    ax.set_xticks(VOLTAGES)
    ax.set_xlim(770, 930) # Padding to match the nice stretch
    
    # Legend - Inside top right to maximize chart area
    ax.legend(loc='upper right', frameon=True, framealpha=0.95, edgecolor='#BDBDBD')
    
    plt.tight_layout()
    
    # Save as high-res 300 DPI
    out_path = os.path.join(RESULTS_BASE, "thesis_jitter_comparison_curve.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved single-pane thesis jitter curve: {out_path}")

if __name__ == "__main__":
    main()
