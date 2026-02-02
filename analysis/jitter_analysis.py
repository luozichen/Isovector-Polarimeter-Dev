#!/usr/bin/env python3
"""
Unified Jitter Analysis Tool

This script provides a single entry point for all jitter analysis methods:
- Trigger-referenced jitter (Method 1)
- Software collimation jitter (Method 2)
- Hardware collimation jitter (Method 3)

Usage:
    # Method 1: Trigger-referenced (single run or range)
    python jitter_analysis.py --method trigger --runs 2-7
    
    # Method 2: Software collimation (single run)
    python jitter_analysis.py --method software --run 17
    python jitter_analysis.py --method software --run 17 --algorithm none
    
    # Method 3: Hardware collimation (6 runs with varying configs)
    python jitter_analysis.py --method hardware --runs 2-7
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import argparse
import os
import sys
import glob
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import config
from analysis.utils import io, plotting
from analysis.utils.physics import gaussian, get_dcfd_time
from analysis.utils.jitter import (
    get_collimation_algorithm,
    solve_jitter_system,
    extract_timing_for_events,
    get_all_pair_variances,
    get_middle_detectors,
    COLLIMATION_ALGORITHMS,
)
from analysis.utils.plotting import DETECTOR_COLORS, PAIR_COLORS


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def fit_gaussian_sigma(data: np.ndarray, bins: int = 40) -> tuple:
    """
    Fits a Gaussian to the data and returns (sigma, popt, bins, counts).
    If fit fails, returns (std_dev, None, bins, counts).
    """
    mean = np.mean(data)
    std = np.std(data)
    
    counts, bin_edges = np.histogram(data, bins=bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    try:
        popt, _ = curve_fit(gaussian, bin_centers, counts, 
                           p0=[np.max(counts), mean, std],
                           maxfev=5000)
        sigma = abs(popt[2])
        return sigma, popt, bin_edges, counts
    except:
        return std, None, bin_edges, counts


# =============================================================================
# METHOD 1: TRIGGER-REFERENCED JITTER
# =============================================================================

def analyze_trigger_jitter_single(run_num: int) -> dict:
    """
    Trigger-referenced jitter analysis for a single run.
    Uses Gaussian fit to determine sigma.
    """
    try:
        time, data, meta = io.load_run_data(run_num)
    except ValueError as e:
        print(f"  Skipping run {run_num}: {e}")
        return None
    
    if not data or len(data) < 4:
        print(f"  Skipping run {run_num}: Need 4 channels")
        return None
    
    run_id = meta.run_id
    config_str = meta.config
    num_events = data[1].shape[0]
    
    print(f"\nProcessing {run_id} (Config: {config_str})")
    print(f"  Events: {num_events}")
    
    results = {}
    positions = ["Top", "Mid1", "Mid2", "Bot"]
    
    for det_id in range(1, 5):
        times = []
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD 
                           for ch in data)
            if is_noise:
                continue
            
            t_val = get_dcfd_time(time, data[det_id][i], config.CFD_FRACTION)
            if not np.isnan(t_val):
                times.append(t_val)
        
        times = np.array(times)
        if len(times) < 10:
            print(f"  Det {det_id}: Not enough data")
            results[det_id] = np.nan
            continue
        
        # Use Gaussian fit
        t_centered = times - np.mean(times)
        sigma, _, _, _ = fit_gaussian_sigma(t_centered * 1e9)  # Convert to ns
        
        pos_idx = config_str.index(str(det_id)) if str(det_id) in config_str else -1
        pos = positions[pos_idx] if pos_idx >= 0 else "?"
        
        print(f"  Det {det_id} [{pos}]: σ = {sigma:.4f} ns")
        results[det_id] = sigma
    
    # Count statistics (using det_id=1 as reference for global stats)
    noise_count = 0
    stats = {} # det_id -> (clean, clipped)
    
    for i in range(num_events):
        is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
        if is_noise:
            noise_count += 1
            
    for det_id in range(1, 5):
        clean = 0
        clipped = 0
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
            if is_noise: continue # Skip noise
            
            t_val = get_dcfd_time(time, data[det_id][i], config.CFD_FRACTION)
            if not np.isnan(t_val):
                clean += 1
            else:
                clipped += 1
        stats[det_id] = (clean, clipped)

    # Save per-run results
    out_path = os.path.join(config.RESULTS_DIR, f"{run_id}_jitter_trigger.txt")
    with open(out_path, "w") as f:
        f.write(f"Trigger-Referenced Jitter Analysis\n")
        f.write(f"Run: {run_id} (Config: {config_str})\n")
        f.write(f"Events: Total={num_events}, Noise={noise_count}\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'Detector':<12} | {'Clean':<8} | {'Clipped':<8} | {'Sigma (ns)':<10}\n")
        f.write("-" * 40 + "\n")
        for det_id in range(1, 5):
            sigma = results[det_id]
            clean, clipped = stats[det_id]
            if np.isnan(sigma):
                f.write(f"Det {det_id:<9} | {clean:<8} | {clipped:<8} | N/A\n")
            else:
                f.write(f"Det {det_id:<9} | {clean:<8} | {clipped:<8} | {sigma:.4f}\n")
    print(f"  Saved: {out_path}")
    
    return {"run_id": run_id, "config": config_str, "sigmas": results}


def analyze_trigger_jitter(run_nums: list):
    print("=" * 60)
    print("METHOD 1: Trigger-Referenced Jitter Analysis")
    print("=" * 60)
    for run_num in run_nums:
        analyze_trigger_jitter_single(run_num)


# =============================================================================
# METHOD 2: SOFTWARE COLLIMATION JITTER
# =============================================================================

def analyze_software_jitter(run_num: int, algorithm_name: str = "landau"):
    print("=" * 60)
    print(f"METHOD 2: Software Collimation Jitter Analysis")
    print(f"Algorithm: {algorithm_name}")
    print("=" * 60)
    
    try:
        time, data, meta = io.load_run_data(run_num)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    run_id = meta.run_id
    config_str = meta.config
    num_events = data[1].shape[0]
    
    print(f"\nRun: {run_id} (Config: {config_str})")
    
    amplitudes = {ch: np.abs(np.min(data[ch], axis=1)) for ch in data}
    algorithm = get_collimation_algorithm(algorithm_name)
    cuts = algorithm.calculate_cuts(amplitudes, config_str)
    
    clean_idx, clipped_idx, noise_idx = algorithm.categorize_events(
        data, amplitudes, cuts, num_events, config_str=config_str
    )
    
    print(f"\nEvent Categories:")
    print(f"  Clean: {len(clean_idx)} ({len(clean_idx)/num_events:.1%})")
    print(f"  Clipped: {len(clipped_idx)}")
    print(f"  Noise: {len(noise_idx)}")
    
    if clipped_idx:
        try:
            plotting.plot_waveforms(
                time, data, clipped_idx, 
                run_id=run_id,
                label=f"Clipped Events ({algorithm_name})",
                suffix=f"clipped_check_{algorithm_name}",
                max_plots=5
            )
            print(f"  Saved visual check: {os.path.join(config.RESULTS_DIR, f'{run_id}_clipped_check_{algorithm_name}.png')}")
        except Exception as e:
            print(f"  Warning: Could not plot clipped check: {e}")
            
    if len(clean_idx) < 10:
        print("Error: Not enough clean events")
        return
        
    times = extract_timing_for_events(time, data, clean_idx)
    
    # Use Gaussian Fit for Pair Variances
    pairs = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    pair_variances = []
    
    for pair in pairs:
        tA = times[pair[0]]
        tB = times[pair[1]]
        mask = (~np.isnan(tA)) & (~np.isnan(tB))
        delta_t = (tA[mask] - tB[mask]) * 1e9
        
        if len(delta_t) < 5:
            pair_variances.append(np.nan)
        else:
            sigma, _, _, _ = fit_gaussian_sigma(delta_t)
            pair_variances.append(sigma**2)
            
    result = solve_jitter_system(pair_variances)
    result.sigmas = np.sqrt(result.sigmas**2) # Make sure it's valid
    
    print("-" * 40)
    for i, sigma in enumerate(result.sigmas):
        print(f"  Det {i+1}: {sigma:.4f} ns")
    print("-" * 40)
    
    # Save results
    out_path = os.path.join(config.RESULTS_DIR, f"{run_id}_jitter_software_{algorithm_name}.txt")
    with open(out_path, "w") as f:
        f.write(f"Software Collimation Jitter Analysis\n")
        f.write(f"Run: {run_id} (Config: {config_str})\n")
        f.write(f"Algorithm: {algorithm_name}\n")
        f.write(f"Events: Total={num_events}, Clean={len(clean_idx)}, Clipped={len(clipped_idx)}, Noise={len(noise_idx)}\n")
        f.write("-" * 40 + "\n")
        for i, sigma in enumerate(result.sigmas):
            det_id = i + 1
            f.write(f"Det {det_id}: {sigma:.4f} ns\n")
    print(f"Saved: {out_path}")


# =============================================================================
# METHOD 3: HARDWARE COLLIMATION JITTER
# =============================================================================

def analyze_hardware_jitter(run_nums: list):
    print("=" * 60)
    print("METHOD 3: Hardware Collimation Jitter Analysis")
    print("=" * 60)
    
    A_matrix = []
    B_vector = []
    pair_info = []
    plot_data = []
    
    for run_num in run_nums:
        try:
            time, data, meta = io.load_run_data(run_num)
        except:
            continue
            
        run_id = meta.run_id
        config_str = meta.config
        detA, detB = get_middle_detectors(config_str)
        
        print(f"\nProcessing {run_id} ({config_str}) -> Pair: {detA}-{detB}")
        
        num_events = data[1].shape[0]
        delta_ts = []
        
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
            if is_noise: continue
            
            tA = get_dcfd_time(time, data[detA][i], config.CFD_FRACTION)
            tB = get_dcfd_time(time, data[detB][i], config.CFD_FRACTION)
            
            if not np.isnan(tA) and not np.isnan(tB):
                delta_ts.append((tA - tB) * 1e9)
        
        delta_ts = np.array(delta_ts)
        if len(delta_ts) < 10: continue
        
        # Use Gaussian Fit (Crucial improvement over std)
        sigma_pair, popt, _, _ = fit_gaussian_sigma(delta_ts)
        
        print(f"  σ(Δt) = {sigma_pair:.4f} ns")
        
        row = [0, 0, 0, 0]
        row[detA-1] = 1
        row[detB-1] = 1
        A_matrix.append(row)
        B_vector.append(sigma_pair**2)
        pair_info.append((run_id, detA, detB, sigma_pair))
        plot_data.append((run_id, detA, detB, delta_ts, sigma_pair, popt))
        
    if len(A_matrix) < 4: return
    
    # Solve system
    from scipy.optimize import lsq_linear
    res = lsq_linear(np.array(A_matrix), np.array(B_vector), bounds=(0, np.inf))
    sigmas = np.sqrt(res.x)
    
    print("\n" + "-" * 40)
    print("Intrinsic Jitter Results (σ):")
    for i, s in enumerate(sigmas):
        print(f"  Detector {i+1}: {s:.4f} ns")
    print("-" * 40)
    
    # Validation Table
    print(f"\n{'Pair':<12} | {'Measured':<12} | {'Predicted':<12} | {'Diff':<12}")
    y_pred = np.array(A_matrix) @ (sigmas**2)
    s_pred = np.sqrt(y_pred)
    for i, (rid, dA, dB, s_meas) in enumerate(pair_info):
        print(f"Det {dA}-{dB:<6} | {s_meas:.4f} ns    | {s_pred[i]:.4f} ns    | {s_meas - s_pred[i]:+.4f} ns")
        
    # Plotting
    n = len(plot_data)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    axes = axes.flatten() if n > 1 else [axes]
    
    fig.suptitle("Hardware Collimation Jitter (Golden Pairs)", fontsize=14, fontweight='bold')
    
    for i, (rid, dA, dB, dt, sigma, popt) in enumerate(plot_data):
        ax = axes[i]
        c = PAIR_COLORS[i % len(PAIR_COLORS)]
        cnt, bins, _ = ax.hist(dt, bins=40, density=True, alpha=0.6, color=c)
        
        if popt is not None:
             x = np.linspace(bins[0], bins[-1], 100)
             ax.plot(x, gaussian(x, *popt), 'k--', lw=1.5)
             
        ax.set_title(f"{rid}: Det {dA}-{dB}\nσ = {sigma:.3f} ns")
        ax.set_xlabel("Δt (ns)")
        ax.grid(True, alpha=0.3)
        
    for i in range(n, len(axes)): axes[i].set_visible(False)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(config.RESULTS_DIR, "jitter_hardware_method.png"))
    
    with open(os.path.join(config.RESULTS_DIR, "jitter_hardware_results.txt"), "w") as f:
        f.write("Hardware Collimation Jitter (Method 3)\n")
        for i, s in enumerate(sigmas):
            f.write(f"Det {i+1}: {s:.4f} ns\n")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def parse_run_range(run_str: str) -> list:
    """Parse run specification like '2-7' or '17' or '2,3,4'."""
    runs = []
    for part in run_str.split(','):
        if '-' in part:
            start, end = part.split('-')
            runs.extend(range(int(start), int(end) + 1))
        else:
            runs.append(int(part))
    return sorted(set(runs))


def main():
    parser = argparse.ArgumentParser(
        description="Unified Jitter Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Methods:
  trigger   - Trigger-referenced jitter (Method 1)
  software  - Software collimation per run (Method 2)
  hardware  - Hardware collimation over 6 runs (Method 3)

Examples:
  python jitter_analysis.py --method trigger --runs 2-7
  python jitter_analysis.py --method software --run 17
  python jitter_analysis.py --method software --run 17 --algorithm none
  python jitter_analysis.py --method hardware --runs 2-7
        """
    )
    
    parser.add_argument('--method', '-m', required=True,
                        choices=['trigger', 'software', 'hardware'],
                        help='Analysis method to use')
    parser.add_argument('--run', '-r', type=int,
                        help='Single run number (for software method)')
    parser.add_argument('--runs', type=str,
                        help='Run range (e.g., "2-7" or "2,3,4")')
    parser.add_argument('--algorithm', '-a', default='type_a',
                        choices=list(COLLIMATION_ALGORITHMS.keys()),
                        help='Collimation algorithm for software method')
    
    args = parser.parse_args()
    
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    
    if args.method == 'trigger':
        if not args.runs and not args.run:
            print("Error: --runs or --run required for trigger method")
            sys.exit(1)
        if args.run:
            run_nums = [args.run]
        else:
            run_nums = parse_run_range(args.runs)
        analyze_trigger_jitter(run_nums)
        
    elif args.method == 'software':
        if not args.run and not args.runs:
            print("Error: --run or --runs required for software method")
            sys.exit(1)
        if args.run:
            run_nums = [args.run]
        else:
            run_nums = parse_run_range(args.runs)
        for run_num in run_nums:
            analyze_software_jitter(run_num, args.algorithm)
        
    elif args.method == 'hardware':
        if not args.runs:
            print("Error: --runs required for hardware method")
            sys.exit(1)
        run_nums = parse_run_range(args.runs)
        analyze_hardware_jitter(run_nums)


if __name__ == "__main__":
    main()
