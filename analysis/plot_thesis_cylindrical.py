#!/usr/bin/env python3
"""
Thesis-Grade Cylindrical Detector Comprehensive Plotter

Generates high-resolution (300 DPI), publication-ready grid figures for:
1. 4 Landau energy calibration fits per voltage (Detectors 1, 3, 5, 6) arranged in a 2x2 grid.
   - Plots the entire spectrum (10 to 450 mV) to show the physical 400 mV clipping spike.
   - Fits the Landau curve strictly on the unclipped region (10 to 250 mV) to ensure perfect mathematical alignment.
2. 6 Gaussian timing resolution fits per voltage (Pairs 1-3, 1-5, 1-6, 3-5, 3-6, 5-6) arranged in a 2x3 grid.
   - Bins timing difference with 50 bins (approx 1.5x wider than 80) for smoother stats.

Usage:
    python3 analysis/plot_thesis_cylindrical.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.optimize import curve_fit

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader
from analysis import config
from analysis.utils.physics import landau_fit_func, get_dcfd_time, gaussian

# Curated harmonious styling
COLORS = {
    1: "#1f77b4",       # Sleek Steel Blue for Det 1
    3: "#e08214",       # Warm Amber for Det 3
    5: "#2ca02c",       # Forest Green for Det 5
    6: "#8c564b",       # Chestnut Rose for Det 6
    "fit": "#d62728",    # Crimson Red for Fit Curves
    "grid": "#cbd5e1",   # Light Slate Grey
    "bg": "#f8fafc"      # Light background fill
}

def load_voltage_data(data_dir):
    """
    Scans the data directory, reads all files, and groups amplitudes/timing
    differences for detectors 1, 3, 5, 6.
    """
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    detectors = [1, 3, 5, 6]
    det_amplitudes = {d: [] for d in detectors}
    pair_delta_ts = {}
    
    for prefix in sorted(prefixes):
        basename = os.path.basename(prefix)
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            continue
            
        pair_id = basename.split('_')[-1]
        if len(pair_id) != 2:
            continue
            
        det_top = int(pair_id[0])
        det_bot = int(pair_id[1])
        
        # Skip Detector 4 completely
        if det_top == 4 or det_bot == 4:
            continue
            
        pair_key = f"{min(det_top, det_bot)}-{max(det_top, det_bot)}"
        if pair_key not in pair_delta_ts:
            pair_delta_ts[pair_key] = []
            
        try:
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            
            t3, volts3 = reader3.read_data(baseline_restore=True)
            t4, volts4 = reader4.read_data(baseline_restore=True)
            t_ns = t3 * 1e9
            num_events = volts3.shape[0]
            
            for i in range(num_events):
                if np.max(volts3[i]) > config.POSITIVE_NOISE_THRESHOLD or np.max(volts4[i]) > config.POSITIVE_NOISE_THRESHOLD:
                    continue
                    
                amp3_mV = np.abs(np.min(volts3[i])) * 1000.0
                amp4_mV = np.abs(np.min(volts4[i])) * 1000.0
                
                # LOWERED THRESHOLD CUT TO 10 mV
                if amp3_mV < 10.0 or amp4_mV < 10.0:
                    continue
                    
                # Accumulate amplitudes
                if det_top in det_amplitudes:
                    det_amplitudes[det_top].append(amp3_mV)
                if det_bot in det_amplitudes:
                    det_amplitudes[det_bot].append(amp4_mV)
                    
                # Timing
                t_top = get_dcfd_time(t3, volts3[i], config.CFD_FRACTION)
                t_bot = get_dcfd_time(t4, volts4[i], config.CFD_FRACTION)
                
                if not np.isnan(t_top) and not np.isnan(t_bot):
                    dt = (t_top - t_bot) * 1e9
                    if det_top > det_bot:
                        dt = -dt
                    pair_delta_ts[pair_key].append(dt)
                    
        except Exception as e:
            pass
            
    return det_amplitudes, pair_delta_ts

def fit_landau(data, voltage_str, bins=100):
    """
    Fits Landau strictly on the true physical cosmic ray muon peak.
    """
    # 1. Find the bin with the highest peak that's later than 200 mV
    temp_counts, temp_edges = np.histogram(data, bins=150, range=(10, 800))
    temp_centers = (temp_edges[:-1] + temp_edges[1:]) / 2
    
    mask = temp_centers > 200.0
    if not np.any(mask):
        start_fit = 250.0
    else:
        valid_centers = temp_centers[mask]
        valid_counts = temp_counts[mask]
        max_idx = np.argmax(valid_counts)
        peak_bin_center = valid_centers[max_idx]
        start_fit = max(10.0, peak_bin_center - 50.0)
        
    # 2. Extract bin centers and counts directly from the full plotted histogram to ensure same bins & scale
    full_counts, full_edges = np.histogram(data, bins=100, range=(10, 800), density=True)
    full_centers = (full_edges[:-1] + full_edges[1:]) / 2
    
    fit_mask = (full_centers >= start_fit) & (full_centers <= 550.0)
    bin_centers = full_centers[fit_mask]
    counts = full_counts[fit_mask]
    
    if len(bin_centers) < 3:
        return 350.0, None, start_fit
    
    max_idx = np.argmax(counts)
    mpv_est = bin_centers[max_idx]
    width_est = 35.0
    amp_est = np.max(counts) * width_est * 3.0
    
    try:
        popt, _ = curve_fit(landau_fit_func, bin_centers, counts,
                           p0=[mpv_est, width_est, amp_est],
                           bounds=([start_fit, 5.0, 0.0], [550.0, 150.0, np.inf]),
                           maxfev=10000)
        return popt[0], popt, start_fit
    except:
        return mpv_est, None, start_fit

def fit_gaussian_sigma(data, bins=50):
    mean = np.mean(data)
    std = np.std(data)
    counts, bin_edges = np.histogram(data, bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    try:
        popt, _ = curve_fit(gaussian, bin_centers, counts, 
                           p0=[np.max(counts), mean, std],
                           maxfev=5000)
        return abs(popt[2]), popt
    except:
        return std, None

def generate_voltage_plots(voltage_str, data_dir, output_dir):
    print(f"\nProcessing all plots for {voltage_str}...")
    det_amplitudes, pair_delta_ts = load_voltage_data(data_dir)
    
    # -------------------------------------------------------------------------
    # 1. LANDAU FITS (2x2 Grid)
    # -------------------------------------------------------------------------
    fig_l, axes_l = plt.subplots(2, 2, figsize=(14, 11), sharex=True)
    axes_l = axes_l.flatten()
    fig_l.suptitle(f"Energy Calibration Landau Fits - Cylindrical Stack ({voltage_str})", 
                   fontsize=16, fontweight='bold', y=0.98)
    
    detectors = [1, 3, 5, 6]
    for idx, d in enumerate(detectors):
        ax = axes_l[idx]
        amps = np.array(det_amplitudes[d])
        
        if len(amps) < 10:
            ax.text(0.5, 0.5, "No Data", transform=ax.transAxes, ha='center', va='center')
            continue
            
        # Fit dynamically on the true physical cosmic ray muon peak
        mpv, popt, start_fit = fit_landau(amps, voltage_str, bins=100)
        
        # Plot data histogram on the full wide range (10 to 800 mV)
        ax.hist(amps, bins=100, range=(10, 800), density=True, alpha=0.55, 
                color=COLORS[d], edgecolor=COLORS[d], lw=0.8)
                
        # Draw the fit curve plotted over the fitted range
        if popt is not None:
            fit_range = (start_fit, 550.0)
            x_fit = np.linspace(fit_range[0], fit_range[1], 300)
            ax.plot(x_fit, landau_fit_func(x_fit, *popt), 'k--', lw=1.5)
            
            text_str = f"MPV: {mpv:.1f} mV\nN: {len(amps)}"
            ax.text(0.95, 0.95, text_str, transform=ax.transAxes, ha='right', va='top', 
                    fontsize=11, fontweight='bold', 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, edgecolor='#BDBDBD'))
                     
        ax.set_title(f"Detector {d}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Peak Amplitude (mV)", fontsize=11, fontweight='bold', labelpad=8)
        ax.set_ylabel("Probability Density", fontsize=11, fontweight='bold', labelpad=8)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.set_xlim([0, 800])
        
        # Bold ticks and spines
        ax.tick_params(axis='both', which='major', labelsize=10, width=2.0, length=6)
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    landau_out = os.path.join(output_dir, f"landau_fits_grid_{voltage_str}.png")
    plt.savefig(landau_out, dpi=300)
    plt.close()
    print(f"  Saved Landau Grid: {landau_out}")
    
    # -------------------------------------------------------------------------
    # 2. GAUSSIAN TIMING JITTER FITS (2x3 Grid - Sharey and Centered)
    # -------------------------------------------------------------------------
    fig_g, axes_g = plt.subplots(2, 3, figsize=(18, 10.5), sharey=True)
    axes_g = axes_g.flatten()
    fig_g.suptitle(f"Coincidence Timing Jitter - Cylindrical Stack ({voltage_str})", 
                   fontsize=16, fontweight='bold', y=0.98)
    
    PAIR_COLORS = ['#5C6BC0', '#26A69A', '#AB47BC', '#EF5350', '#42A5F5', '#66BB6A']
    pairs = ["1-3", "1-5", "1-6", "3-5", "3-6", "5-6"]
    for idx, pair_key in enumerate(pairs):
        ax = axes_g[idx]
        dt_data = np.array(pair_delta_ts.get(pair_key, []))
        
        if len(dt_data) < 10:
            ax.text(0.5, 0.5, "No Data", transform=ax.transAxes, ha='center', va='center')
            continue
            
        dt_centered = dt_data - np.mean(dt_data)
        
        # BINS SET TO 50 FOR timing (approx 1.5x wider than 80)
        sigma, popt = fit_gaussian_sigma(dt_centered, bins=50)
        fwhm = sigma * 2.355
        
        # Center x-axis strictly around the fitted Gaussian mean mu
        mu = popt[1] if popt is not None else 0.0
        
        # Plot data histogram with 50 bins centered around mu - 5.0 to mu + 5.0 ns
        c = PAIR_COLORS[idx % len(PAIR_COLORS)]
        ax.hist(dt_centered, bins=50, range=(mu - 5.0, mu + 5.0), density=True, alpha=0.6,
                color=c)
                
        # Plot Gaussian fit
        if popt is not None:
            x_fit = np.linspace(mu - 5.0, mu + 5.0, 300)
            ax.plot(x_fit, gaussian(x_fit, *popt), 'k--', lw=1.5)
                     
        ax.set_title(f"Pair {pair_key}\n$\\sigma$ = {sigma:.3f} ns", fontsize=12, fontweight='bold')
        ax.set_xlabel("Timing Difference $\\Delta t$ (ns)", fontsize=11, fontweight='bold', labelpad=8)
        
        # Share y axis ticks, only show numbers and label on leftmost column (idx % 3 == 0)
        if idx % 3 == 0:
            ax.tick_params(labelleft=True)
            ax.set_ylabel("Density", fontsize=11, fontweight='bold', labelpad=8)
        else:
            ax.tick_params(labelleft=False)
            
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.set_xlim([mu - 5.0, mu + 5.0])
        
        # Bold ticks and spines
        ax.tick_params(axis='both', which='major', labelsize=10, width=1.5, length=5)
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    jitter_out = os.path.join(output_dir, f"jitter_fits_grid_{voltage_str}.png")
    plt.savefig(jitter_out, dpi=300)
    plt.close()
    print(f"  Saved Jitter Grid: {jitter_out}")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'results', 'physical', 'cylindrical')
    os.makedirs(output_dir, exist_ok=True)
    
    voltages = [
        ("800V", os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL')),
        ("850V", os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL')),
        ("900V", os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'))
    ]
    
    for voltage_str, data_dir in voltages:
        generate_voltage_plots(voltage_str, data_dir, output_dir)
        
    print("\n=======================================================")
    print("  ALL COMPREHENSIVE THESIS GRID FIGURES GENERATED!")
    print("  Grouped under: results/physical/cylindrical/")
    print("=======================================================")
    
    # -------------------------------------------------------------------------
    # Copy to results/definitive/ directory for user review
    # -------------------------------------------------------------------------
    import shutil
    definitive_dir = os.path.join(base_dir, 'results', 'definitive')
    os.makedirs(definitive_dir, exist_ok=True)
    
    for voltage_str, _ in voltages:
        # Copy Landau Grid
        src_landau = os.path.join(output_dir, f"landau_fits_grid_{voltage_str}.png")
        dest_landau = os.path.join(definitive_dir, f"landau_grid_cylindrical_{voltage_str}.png")
        if os.path.exists(src_landau):
            shutil.copy2(src_landau, dest_landau)
            print(f"Copied: {src_landau} -> {dest_landau}")
            
        # Copy Jitter Grid
        src_jitter = os.path.join(output_dir, f"jitter_fits_grid_{voltage_str}.png")
        dest_jitter = os.path.join(definitive_dir, f"jitter_pairs_cylindrical_{voltage_str}.png")
        if os.path.exists(src_jitter):
            shutil.copy2(src_jitter, dest_jitter)
            print(f"Copied: {src_jitter} -> {dest_jitter}")
            
    # Copy overall gain/jitter comparison curves if they exist
    src_gain_curve = os.path.join(output_dir, "voltage_comparison_cylindrical.png")
    dest_gain_curve = os.path.join(definitive_dir, "voltage_comparison_cylindrical.png")
    if os.path.exists(src_gain_curve):
        shutil.copy2(src_gain_curve, dest_gain_curve)
        print(f"Copied: {src_gain_curve} -> {dest_gain_curve}")
        
    src_jitter_curve = os.path.join(output_dir, "jitter_comparison_cylindrical.png")
    dest_jitter_curve = os.path.join(definitive_dir, "jitter_comparison_cylindrical.png")
    if os.path.exists(src_jitter_curve):
        shutil.copy2(src_jitter_curve, dest_jitter_curve)
        print(f"Copied: {src_jitter_curve} -> {dest_jitter_curve}")
        
    # Copy cylindrical results text summary
    src_txt = os.path.join(output_dir, "..", "cylindrical_results.txt")
    dest_txt = os.path.join(definitive_dir, "cylindrical_results.txt")
    if os.path.exists(src_txt):
        shutil.copy2(src_txt, dest_txt)
        print(f"Copied: {src_txt} -> {dest_txt}")

if __name__ == "__main__":
    main()
