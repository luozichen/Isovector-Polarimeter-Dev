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

RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results")

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
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("New Detectors: Gain & Jitter vs Working Voltage", fontsize=16, fontweight='bold')
    
    # Left panel: MPV vs Voltage
    ax1.set_title("Gain (Landau MPV) vs Voltage", fontweight='bold')
    for det in range(1, 5):
        voltages_present = []
        mpvs = []
        for v, v_num in zip(VOLTAGES, VOLTAGE_NUMS):
            if v in all_results and det in all_results[v]["mpvs"]:
                voltages_present.append(v_num)
                mpvs.append(all_results[v]["mpvs"][det])
        
        if voltages_present:
            ax1.plot(voltages_present, mpvs, 'o-', color=DETECTOR_COLORS[det],
                     markersize=8, linewidth=2, label=f"Det {det}")
    
    # Overlay old 800V results
    for det in range(1, 5):
        old_mpv = OLD_CALIBRATION[det]["mpv_mV"]
        ax1.plot(800, old_mpv, 's', color=DETECTOR_COLORS[det], markersize=10,
                 markeredgecolor='black', markeredgewidth=1.5, alpha=0.6)
    
    # Add a single legend entry for old markers
    ax1.plot([], [], 's', color='gray', markersize=10,
             markeredgecolor='black', markeredgewidth=1.5, alpha=0.6,
             label='Old Detectors (800V)')
    
    ax1.set_xlabel("Working Voltage (V)", fontsize=12)
    ax1.set_ylabel("MPV (mV)", fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(VOLTAGE_NUMS)
    
    # Right panel: Jitter vs Voltage
    ax2.set_title("Intrinsic Jitter (σ) vs Voltage", fontweight='bold')
    for det in range(1, 5):
        voltages_present = []
        sigs = []
        for v, v_num in zip(VOLTAGES, VOLTAGE_NUMS):
            if v in all_results:
                voltages_present.append(v_num)
                sigs.append(all_results[v]["sigmas"][det - 1])
        
        if voltages_present:
            ax2.plot(voltages_present, sigs, 'o-', color=DETECTOR_COLORS[det],
                     markersize=8, linewidth=2, label=f"Det {det}")
    
    # Overlay old 800V jitter
    for det in range(1, 5):
        old_sig = OLD_JITTER[det]
        ax2.plot(800, old_sig, 's', color=DETECTOR_COLORS[det], markersize=10,
                 markeredgecolor='black', markeredgewidth=1.5, alpha=0.6)
    
    ax2.plot([], [], 's', color='gray', markersize=10,
             markeredgecolor='black', markeredgewidth=1.5, alpha=0.6,
             label='Old Detectors (800V)')
    
    ax2.set_xlabel("Working Voltage (V)", fontsize=12)
    ax2.set_ylabel("σ (ns)", fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(VOLTAGE_NUMS)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.94])
    out_path = os.path.join(RESULTS_BASE, "voltage_comparison.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"\nSaved comparison plot: {out_path}")
    
    # =========================================================================
    # Summary Table
    # =========================================================================
    summary_path = os.path.join(RESULTS_BASE, "voltage_comparison_summary.txt")
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
