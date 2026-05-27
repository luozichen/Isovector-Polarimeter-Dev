#!/usr/bin/env python3
"""
Run Stable Voltage Comparison

Runs the combined analysis for all three voltages (800V, 850V, 900V),
then produces cross-voltage comparison plots:
  1. Gain (MPV) vs Voltage for each detector
  2. Intrinsic Jitter (σ) vs Voltage for each detector
  3. Overlay with old detector results for 800V

Usage:
    python analyse_stable_voltage_comparison.py
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SCRIPT_DIR)  # For sibling module import

from analysis import config

# Import the combined analysis driver
from analyse_stable_combined import analyze_combined

RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results_corrected")

DETECTOR_COLORS = {
    1: '#E57373',
    2: '#64B5F6',
    3: '#81C784',
    4: '#FFB74D',
}

OLD_CALIBRATION = config.CALIBRATION
OLD_JITTER = config.JITTER_SIGMA_NS

VOLTAGES = ["800V", "850V", "900V"]
VOLTAGE_NUMS = [800, 850, 900]  # For plotting x-axis


def main():
    os.makedirs(RESULTS_BASE, exist_ok=True)
    
    # Run combined analysis for each voltage
    all_results = {}
    for v in VOLTAGES:
        print(f"\n{'#'*60}")
        print(f"# Processing {v}")
        print(f"{'#'*60}")
        r = analyze_combined(v)
        if r:
            all_results[v] = r
    
    if len(all_results) < 2:
        print("Need at least 2 voltages for comparison. Exiting.")
        return
    
    # =========================================================================
    # Comparison Plots
    # =========================================================================
    
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
    
    fig, ax1 = plt.subplots(figsize=(12, 9))
    
    # Left panel: MPV vs Voltage
    ax1.set_title("Gain (Landau MPV) vs HV Operating Voltage", pad=20)
    for det in range(1, 5):
        voltages_present = []
        mpvs = []
        for v, v_num in zip(VOLTAGES, VOLTAGE_NUMS):
            if v in all_results and det in all_results[v]["mpvs"]:
                voltages_present.append(v_num)
                mpvs.append(all_results[v]["mpvs"][det])
        
        if voltages_present:
            ax1.plot(voltages_present, mpvs, 'o-', color=DETECTOR_COLORS[det],
                     markersize=12, linewidth=3.5, label=f"Det {det} (New PCB)")
    
    # Overlay old 800V results
    for det in range(1, 5):
        old_mpv = OLD_CALIBRATION[det]["mpv_mV"]
        ax1.plot(800, old_mpv, 's', color=DETECTOR_COLORS[det], markersize=14,
                 markeredgecolor='black', markeredgewidth=2.0, alpha=0.45)
    
    # Add a single legend entry for old markers
    ax1.plot([], [], 's', color='gray', markersize=12,
             markeredgecolor='black', markeredgewidth=2.0, alpha=0.45,
             label='Old Baseline (v2.2 @ 800V)')
    
    ax1.set_xlabel("HV Operating Voltage (V)", labelpad=12)
    ax1.set_ylabel("Gain (Landau MPV in mV)", labelpad=12)
    
    # Spines/Border Aesthetics
    for spine in ax1.spines.values():
        spine.set_linewidth(2.5)
        
    ax1.grid(True, alpha=0.25, linestyle='-', linewidth=1.5)
    ax1.set_xticks(VOLTAGE_NUMS)
    ax1.set_xlim(770, 930) # Padding to match the nice stretch
    
    ax1.legend(loc='upper left', frameon=True, framealpha=0.95, edgecolor='#BDBDBD')
    
    plt.tight_layout()
    out_path = os.path.join(RESULTS_BASE, "voltage_comparison_corrected.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\nSaved comparison plot: {out_path}")
    
    # =========================================================================
    # Summary Table
    # =========================================================================
    summary_path = os.path.join(RESULTS_BASE, "voltage_comparison_summary_corrected.txt")
    with open(summary_path, "w") as f:
        f.write("Voltage Comparison Summary (New Detectors)\n")
        f.write("=" * 70 + "\n\n")
        
        # MPV Table
        f.write("Gain (MPV in mV):\n")
        header = f"{'Det':<6}"
        for v in VOLTAGES:
            header += f" | {v:>10}"
        header += f" | {'Old 800V':>10}"
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")
        
        for det in range(1, 5):
            row = f"  {det:<4}"
            for v in VOLTAGES:
                if v in all_results and det in all_results[v]["mpvs"]:
                    row += f" | {all_results[v]['mpvs'][det]:>8.1f} mV"
                else:
                    row += f" | {'N/A':>10}"
            row += f" | {OLD_CALIBRATION[det]['mpv_mV']:>8.1f} mV"
            f.write(row + "\n")
        
        f.write("\n")
        
        # Jitter Table
        f.write("Intrinsic Jitter (σ in ns):\n")
        header = f"{'Det':<6}"
        for v in VOLTAGES:
            header += f" | {v:>10}"
        header += f" | {'Old 800V':>10}"
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")
        
        for det in range(1, 5):
            row = f"  {det:<4}"
            for v in VOLTAGES:
                if v in all_results:
                    row += f" | {all_results[v]['sigmas'][det-1]:>8.4f} ns"
                else:
                    row += f" | {'N/A':>10}"
            row += f" | {OLD_JITTER[det]:>8.4f} ns"
            f.write(row + "\n")
    
    print(f"Saved summary: {summary_path}")


if __name__ == "__main__":
    main()
