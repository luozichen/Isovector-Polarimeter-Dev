#!/usr/bin/env python3
"""
Thesis Defense Plot: 850V Combined Jitter (Golden Pairs)
Produces a beautiful 3x2 grid of timing pair distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from analysis import config
from analysis.run_stable_analysis.analyse_stable_combined import discover_configs, load_config_data, get_middle_detectors
from analysis.utils.physics import gaussian, get_dcfd_time

PAIR_COLORS = ['#5C6BC0', '#26A69A', '#AB47BC', '#EF5350', '#42A5F5', '#66BB6A']
RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results")

def main():
    voltage = "850V"
    voltage_dir = os.path.join(config.DATA_DIR, f"run_stable_{voltage}")
    if not os.path.isdir(voltage_dir):
        print(f"Error: {voltage_dir} not found")
        return
        
    output_dir = os.path.join(RESULTS_BASE, voltage)
    os.makedirs(output_dir, exist_ok=True)
    
    configs = discover_configs(voltage_dir)
    print(f"Loading jitter data for 850V from {len(configs)} configs...")
    
    plot_data = []
    
    # 1. Accumulate Jitter Data
    for timestamp, config_str in configs:
        mid1, mid2 = get_middle_detectors(config_str)
        time_arr, data, num_events = load_config_data(voltage_dir, timestamp, config_str)
        if time_arr is None:
            continue
            
        delta_ts = []
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
            if not is_noise:
                tA = get_dcfd_time(time_arr, data[mid1][i], config.CFD_FRACTION)
                tB = get_dcfd_time(time_arr, data[mid2][i], config.CFD_FRACTION)
                if not np.isnan(tA) and not np.isnan(tB):
                    delta_ts.append((tA - tB) * 1e9)
        
        delta_ts = np.array(delta_ts)
        if len(delta_ts) < 10:
            continue
            
        # Use the zoomed range centered on the median for fitting and plotting
        center = np.median(delta_ts)
        plot_range = (center - 5, center + 5)
        dt_core = delta_ts[(delta_ts >= plot_range[0]) & (delta_ts <= plot_range[1])]
        
        counts, bin_edges = np.histogram(dt_core, bins=40, range=plot_range, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        sigma_pair = np.std(dt_core)
        popt = None
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts,
                               p0=[np.max(counts), np.mean(dt_core), sigma_pair], maxfev=5000)
            sigma_pair = abs(popt[2])
        except:
            pass
            
        plot_data.append((config_str, mid1, mid2, dt_core, plot_range, sigma_pair, popt))

    # 2. Thesis Plotting Properties
    plt.rcParams.update({
        'font.size': 14,
        'font.weight': 'bold',
        'axes.titlesize': 20,
        'axes.labelsize': 18,
        'axes.labelweight': 'bold',
        'axes.titleweight': 'bold',
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
    })
    
    # Create 3x2 vertical grid as requested but flatter overall
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    axes = axes.flatten()
    
    for i, (cfg, dA, dB, dt, pl_range, sigma, popt) in enumerate(plot_data):
        if i >= 6: break
        ax = axes[i]
        color = PAIR_COLORS[i % len(PAIR_COLORS)]
        
        # Draw nice histogram
        ax.hist(dt, bins=40, range=pl_range, density=True, alpha=0.7, 
                color=color, edgecolor='black', linewidth=0.5)
        
        if popt is not None:
            x_fine = np.linspace(pl_range[0], pl_range[1], 200)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'k--', lw=2.5)
            
        # Bold borders
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
            
        ax.set_xlim(pl_range)
        ax.set_title(f"Config {cfg}: Det {dA}-{dB} (850V)", pad=15)
        ax.set_xlabel("Δt (ns)", labelpad=8)
        ax.set_ylabel("Density", labelpad=8)
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=1.5)
        
        # Add sigma text box
        textstr = f"σ = {sigma:.3f} ns"
        props = dict(boxstyle='round,pad=0.6', facecolor='white', alpha=0.9, edgecolor='#BDBDBD')
        ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=18,
                verticalalignment='top', horizontalalignment='right', bbox=props)
                
        # Make the plot look flatter by giving it more vertical headroom
        # Reverted multiplier as per user clarification
        current_ylim = ax.get_ylim()
        ax.set_ylim(0, current_ylim[1] * 1.05)

    plt.tight_layout(pad=4.0)
    
    # Save high-res
    out_path = os.path.join(output_dir, "850V_thesis_golden_pairs_jitter.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved thesis jitter plot: {out_path}")

if __name__ == "__main__":
    main()
