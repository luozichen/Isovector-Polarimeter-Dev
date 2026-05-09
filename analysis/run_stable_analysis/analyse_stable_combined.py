#!/usr/bin/env python3
"""
Run Stable Combined Analysis

For each voltage, combines data across all 6 stack configurations to produce:
1. Golden Pairs Jitter (Hardware Collimation Method 3)
   - Uses middle detector pairs from each config
   - Solves the overdetermined system for intrinsic detector jitters
2. Combined Landau Distributions
   - Aggregates middle-position data per detector across configs
   - Fits high-statistics Landau distributions

Usage:
    python analyse_stable_combined.py --voltage 800V
    python analyse_stable_combined.py --all
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, lsq_linear
import os
import sys
import glob
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from analysis import config
from analysis.utils.wfm import WfmReader
from analysis.utils.physics import get_dcfd_time, landau_fit_func, gaussian

# =============================================================================
# Configuration
# =============================================================================

RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results")

VOLTAGE_PARAMS = {
    "800V": {"landau_range": (0.01, 0.4), "bins": 50},
    "850V": {"landau_range": (0.05, 0.5), "bins": 50},
    "900V": {"landau_range": (0.10, 0.6), "bins": 50},
}

DETECTOR_COLORS = {
    1: '#E57373',
    2: '#64B5F6',
    3: '#81C784',
    4: '#FFB74D',
}
PAIR_COLORS = ['#5C6BC0', '#26A69A', '#AB47BC', '#EF5350', '#42A5F5', '#66BB6A']

# Previous results from config.py (old detectors, 800V)
OLD_CALIBRATION = config.CALIBRATION
OLD_JITTER = config.JITTER_SIGMA_NS


# =============================================================================
# Data Loading (shared with analyse_stable.py)
# =============================================================================

def discover_configs(voltage_dir: str) -> list:
    """Discover all (timestamp, config_str) tuples in voltage dir."""
    wfm_files = glob.glob(os.path.join(voltage_dir, "*_Ch*.wfm"))
    configs = {}
    for f in wfm_files:
        basename = os.path.basename(f)
        match = re.match(r'(\d{6}_\d{6})_(\d{4})_Ch(\d+)\.wfm', basename)
        if match:
            timestamp, cfg = match.group(1), match.group(2)
            key = f"{timestamp}_{cfg}"
            if key not in configs:
                configs[key] = (timestamp, cfg)
    return sorted(configs.values(), key=lambda x: x[0])


def load_config_data(voltage_dir: str, timestamp: str, config_str: str):
    """Load 4-channel data for a config. Returns (time, {ch: volts}, num_events)."""
    data = {}
    time = None
    min_events = float('inf')
    
    for ch in range(1, 5):
        filepath = os.path.join(voltage_dir, f"{timestamp}_{config_str}_Ch{ch}.wfm")
        if not os.path.exists(filepath):
            return None, {}, 0
        wfm = WfmReader(filepath)
        t, v = wfm.read_data()
        if time is None:
            time = t
        data[ch] = v
        min_events = min(min_events, v.shape[0])
    
    for ch in data:
        data[ch] = data[ch][:min_events]
    return time, data, min_events


def get_middle_detectors(config_str: str):
    """Return (mid1_id, mid2_id) from a 4-char config string."""
    return int(config_str[1]), int(config_str[2])


# =============================================================================
# Analysis
# =============================================================================

def analyze_combined(voltage: str):
    """Run combined analysis for a voltage setting."""
    voltage_dir = os.path.join(config.DATA_DIR, f"run_stable_{voltage}")
    if not os.path.isdir(voltage_dir):
        print(f"Error: {voltage_dir} not found")
        return None
    
    params = VOLTAGE_PARAMS.get(voltage, VOLTAGE_PARAMS["800V"])
    landau_range = params["landau_range"]
    bins_count = params["bins"]
    
    output_dir = os.path.join(RESULTS_BASE, voltage)
    os.makedirs(output_dir, exist_ok=True)
    
    configs = discover_configs(voltage_dir)
    
    print(f"\n{'='*60}")
    print(f"Combined Analysis: {voltage}")
    print(f"Configs: {[c[1] for c in configs]}")
    print(f"{'='*60}")
    
    # =========================================================================
    # Part 1: Golden Pairs Jitter (Hardware Collimation, Method 3)
    # =========================================================================
    print(f"\n{'—'*40}")
    print("Part 1: Golden Pairs Jitter")
    print(f"{'—'*40}")
    
    A_matrix = []
    B_vector = []
    pair_info = []
    plot_data = []
    
    for timestamp, config_str in configs:
        mid1, mid2 = get_middle_detectors(config_str)
        print(f"\n  Config {config_str} → Middle pair: Det {mid1}-{mid2}")
        
        time_arr, data, num_events = load_config_data(voltage_dir, timestamp, config_str)
        if time_arr is None:
            continue
        
        # Extract timing for middle pair (noise-filtered only, no amplitude cuts)
        delta_ts = []
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
            if is_noise:
                continue
            
            tA = get_dcfd_time(time_arr, data[mid1][i], config.CFD_FRACTION)
            tB = get_dcfd_time(time_arr, data[mid2][i], config.CFD_FRACTION)
            
            if not np.isnan(tA) and not np.isnan(tB):
                delta_ts.append((tA - tB) * 1e9)
        
        delta_ts = np.array(delta_ts)
        if len(delta_ts) < 10:
            print(f"    Too few valid events ({len(delta_ts)})")
            continue
        
        # Gaussian fit for sigma (Original Method 3)
        # Filter strictly to (-10, 10) ns to increase bin density over the central peak
        plot_range = (-10, 10)
        dt_core = delta_ts[(delta_ts >= plot_range[0]) & (delta_ts <= plot_range[1])]
        
        mean_dt = np.mean(dt_core)
        std_dt = np.std(dt_core)
        
        counts, bin_edges = np.histogram(dt_core, bins=40, range=plot_range, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        sigma_pair = std_dt
        popt_gauss = None
        try:
            popt_gauss, _ = curve_fit(gaussian, bin_centers, counts,
                                       p0=[np.max(counts), mean_dt, std_dt], maxfev=5000)
            sigma_pair = abs(popt_gauss[2])
        except Exception as e:
            print(f"    [Warning] Gaussian fit failed: {e}")
        
        print(f"    N = {len(delta_ts)}, σ(Δt) = {sigma_pair:.4f} ns")
        
        # Build system
        row = [0, 0, 0, 0]
        row[mid1 - 1] = 1
        row[mid2 - 1] = 1
        A_matrix.append(row)
        B_vector.append(sigma_pair ** 2)
        pair_info.append((config_str, mid1, mid2, sigma_pair))
        plot_data.append((config_str, mid1, mid2, dt_core, plot_range, sigma_pair, popt_gauss))
    
    if len(A_matrix) < 4:
        print("Error: Not enough valid configs to solve jitter system")
        return None
    
    # Solve system
    A = np.array(A_matrix)
    B = np.array(B_vector)
    res = lsq_linear(A, B, bounds=(0, np.inf))
    sigmas = np.sqrt(res.x)
    
    print(f"\n{'—'*40}")
    print(f"Intrinsic Jitter Results ({voltage}):")
    print(f"{'—'*40}")
    for i, s in enumerate(sigmas):
        print(f"  Det {i+1}: σ = {s:.4f} ns  (FWHM = {s*2.355:.4f} ns)")
    
    # Validation table
    y_pred = A @ (sigmas ** 2)
    s_pred = np.sqrt(y_pred)
    print(f"\n{'Pair':<12} | {'Measured':>10} | {'Predicted':>10} | {'Residual':>10}")
    print("-" * 50)
    for i, (cfg, dA, dB, s_meas) in enumerate(pair_info):
        print(f"  {dA}-{dB} ({cfg}) | {s_meas:>8.4f} ns | {s_pred[i]:>8.4f} ns | {s_meas - s_pred[i]:>+8.4f} ns")
    
    # Plot Golden Pairs timing distributions
    n = len(plot_data)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    fig.suptitle(f"Golden Pairs Jitter — {voltage}", fontsize=14, fontweight='bold')
    
    for i, (cfg, dA, dB, dt, pl_range, sigma, popt) in enumerate(plot_data):
        ax = axes[i]
        c = PAIR_COLORS[i % len(PAIR_COLORS)]
        cnt, bins, _ = ax.hist(dt, bins=40, range=pl_range, density=True, alpha=0.6, color=c)
        
        if popt is not None:
            x_fine = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'k--', lw=1.5)
        
        ax.set_title(f"Config {cfg}: Det {dA}-{dB}\nσ = {sigma:.3f} ns", fontweight='bold')
        ax.set_xlabel("Δt (ns)")
        ax.grid(True, alpha=0.3)
    
    for i in range(n, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    jitter_plot_path = os.path.join(output_dir, f"{voltage}_golden_pairs_jitter.png")
    plt.savefig(jitter_plot_path, dpi=config.DEFAULT_DPI)
    plt.close()
    print(f"\nSaved: {jitter_plot_path}")
    
    # =========================================================================
    # Part 2: Combined Landau (Physical Collimation)
    # =========================================================================
    print(f"\n{'—'*40}")
    print("Part 2: Combined Landau (Middle Positions)")
    print(f"{'—'*40}")
    
    # Accumulate amplitudes per detector (only when in middle position)
    det_middle_amps = {d: [] for d in range(1, 5)}
    det_run_data = {d: [] for d in range(1, 5)}  # for grid plot
    
    for timestamp, config_str in configs:
        mid1, mid2 = get_middle_detectors(config_str)
        
        time_arr, data, num_events = load_config_data(voltage_dir, timestamp, config_str)
        if time_arr is None:
            continue
        
        # Get amplitudes and filter noise
        amplitudes = {ch: np.abs(np.min(data[ch], axis=1)) for ch in data}
        
        for i in range(num_events):
            is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
            if is_noise:
                continue
            
            for det_id in [mid1, mid2]:
                det_middle_amps[det_id].append(amplitudes[det_id][i])
        
        # Store per-run middle data for grid plot
        for det_id in [mid1, mid2]:
            clean_amps = []
            for i in range(num_events):
                is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
                if not is_noise:
                    clean_amps.append(amplitudes[det_id][i])
            det_run_data[det_id].append((config_str, clean_amps))
    
    # Combined Landau fits
    combined_mpvs = {}
    
    # Grid plot: 4 detectors × (up to 3 individual + 1 combined)
    max_individual = 3
    n_cols = max_individual + 1
    # Remove sharex=True so each detector can dynamically scale
    fig, axes = plt.subplots(4, n_cols, figsize=(5 * n_cols, 16))
    plt.subplots_adjust(hspace=0.45, wspace=0.2)
    fig.suptitle(f"Combined Landau: {voltage} (Middle Position Only)", fontsize=16, fontweight='bold')
    
    for det_idx in range(4):
        det_id = det_idx + 1
        runs = det_run_data[det_id]
        combined = det_middle_amps[det_id]
        color = DETECTOR_COLORS[det_id]
        
        # Individual runs (first max_individual)
        for col in range(max_individual):
            ax = axes[det_idx, col]
            if col < len(runs):
                cfg, amps = runs[col]
                amps = np.array(amps)
                y, x, _ = ax.hist(amps, bins=bins_count, range=landau_range,
                                  density=False, histtype='stepfilled', alpha=0.4, color=color)
                bin_centers = (x[:-1] + x[1:]) / 2
                
                if len(amps) > 0 and np.max(y) > 0:
                    peak_idx = np.argmax(y)
                    
                    bin_width = bin_centers[1] - bin_centers[0]
                    width_guess = bin_width * 2
                    amp_guess = np.max(y) * width_guess * np.sqrt(2 * np.pi)
                    try:
                        popt, _ = curve_fit(landau_fit_func, bin_centers, y,
                                            p0=[bin_centers[peak_idx], width_guess, amp_guess],
                                            bounds=([0, 1e-4, 0], [2, 1, np.inf]),
                                            maxfev=10000)
                        x_fine = np.linspace(landau_range[0], landau_range[1], 200)
                        ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=1.5)
                        # Zoom in nicely around the fitted MPV
                        ax.set_xlim(max(0, popt[0] - 0.08), min(landau_range[1], popt[0] + 0.18))
                        
                        ax.text(0.95, 0.95, f"MPV: {popt[0]*1000:.1f} mV\nN: {len(amps)}",
                                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
                    except Exception as e:
                        print(f"    [Warning] Det {det_id} @ {cfg} fit failed: {e}")
                        ax.text(0.95, 0.95, f"Fit Failed\nN: {len(amps)}",
                                transform=ax.transAxes, ha='right', va='top', fontsize=9, color='red')
                
                ax.set_title(f"Det {det_id} @ {cfg}", fontsize=10)
            else:
                ax.axis('off')
            
            if det_idx == 3:
                ax.set_xlabel("Amplitude (V)")
            if col == 0:
                ax.set_ylabel("Counts")
            ax.grid(True, alpha=0.3)
        
        # Combined column
        ax_comb = axes[det_idx, max_individual]
        combined_arr = np.array(combined)
        
        y, x, _ = ax_comb.hist(combined_arr, bins=bins_count, range=landau_range,
                                density=False, histtype='stepfilled', alpha=0.4, color='purple')
        bin_centers = (x[:-1] + x[1:]) / 2
        
        if len(combined_arr) > 0 and np.max(y) > 0:
            peak_idx = np.argmax(y)
            
            bin_width = bin_centers[1] - bin_centers[0]
            width_guess = bin_width * 2
            amp_guess = np.max(y) * width_guess * np.sqrt(2 * np.pi)
            try:
                popt, _ = curve_fit(landau_fit_func, bin_centers, y,
                                    p0=[bin_centers[peak_idx], width_guess, amp_guess],
                                    bounds=([0, 1e-4, 0], [2, 1, np.inf]),
                                    maxfev=10000)
                x_fine = np.linspace(landau_range[0], landau_range[1], 200)
                ax_comb.plot(x_fine, landau_fit_func(x_fine, *popt), 'k--', lw=1.5)
                # Zoom in nicely around the fitted MPV
                ax_comb.set_xlim(max(0, popt[0] - 0.08), min(landau_range[1], popt[0] + 0.18))
                
                mpv_mV = popt[0] * 1000
                combined_mpvs[det_id] = mpv_mV
                ax_comb.text(0.95, 0.95, f"MPV: {mpv_mV:.1f} mV\nN: {len(combined_arr)}",
                             transform=ax_comb.transAxes, ha='right', va='top', fontsize=9,
                             bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
                print(f"  Det {det_id}: Combined MPV = {mpv_mV:.1f} mV (N = {len(combined_arr)})")
            except Exception as e:
                print(f"  Det {det_id}: Combined fit failed: {e}")
        
        ax_comb.set_title(f"Det {det_id} Combined", fontsize=10, fontweight='bold')
        ax_comb.grid(True, alpha=0.3)
        if det_idx == 3:
            ax_comb.set_xlabel("Amplitude (V)")
    
    landau_plot_path = os.path.join(output_dir, f"{voltage}_combined_landau_grid.png")
    plt.savefig(landau_plot_path, dpi=config.DEFAULT_DPI)
    plt.close()
    print(f"\nSaved: {landau_plot_path}")
    
    # =========================================================================
    # Summary & Comparison with Old Results
    # =========================================================================
    print(f"\n{'='*60}")
    print(f"Summary: {voltage}")
    print(f"{'='*60}")
    
    if voltage == "800V":
        print(f"\n{'Det':<6} | {'New MPV':>10} | {'Old MPV':>10} | {'Δ MPV':>8} | "
              f"{'New σ':>8} | {'Old σ':>8} | {'Δσ':>8}")
        print("-" * 75)
        for det in range(1, 5):
            new_mpv = combined_mpvs.get(det, float('nan'))
            old_mpv = OLD_CALIBRATION[det]["mpv_mV"]
            new_sig = sigmas[det - 1]
            old_sig = OLD_JITTER[det]
            print(f"  {det:<4} | {new_mpv:>8.1f} mV | {old_mpv:>8.1f} mV | "
                  f"{new_mpv - old_mpv:>+7.1f} | "
                  f"{new_sig:>6.4f} ns | {old_sig:>6.4f} ns | "
                  f"{new_sig - old_sig:>+7.4f}")
    else:
        print(f"\n{'Det':<6} | {'MPV (mV)':>10} | {'σ (ns)':>10} | {'FWHM (ns)':>10}")
        print("-" * 50)
        for det in range(1, 5):
            mpv = combined_mpvs.get(det, float('nan'))
            sig = sigmas[det - 1]
            print(f"  {det:<4} | {mpv:>8.1f} mV | {sig:>8.4f} | {sig*2.355:>8.4f}")
    
    # Save combined results
    results_path = os.path.join(output_dir, f"{voltage}_combined_results.txt")
    with open(results_path, "w") as f:
        f.write(f"Combined Analysis Results: {voltage}\n")
        f.write(f"{'='*60}\n\n")
        
        f.write("Combined Landau MPVs (Middle Position, Physical Collimation):\n")
        for det in range(1, 5):
            mpv = combined_mpvs.get(det, float('nan'))
            f.write(f"  Det {det}: {mpv:.1f} mV\n")
        
        f.write(f"\nGolden Pairs Jitter ({len(pair_info)} configs):\n")
        for i, s in enumerate(sigmas):
            f.write(f"  Det {i+1}: σ = {s:.4f} ns  (FWHM = {s*2.355:.4f} ns)\n")
        
        f.write(f"\nValidation (Measured vs Predicted pair σ):\n")
        for i, (cfg, dA, dB, s_meas) in enumerate(pair_info):
            f.write(f"  {dA}-{dB} ({cfg}): measured={s_meas:.4f}, "
                    f"predicted={s_pred[i]:.4f}, Δ={s_meas - s_pred[i]:+.4f} ns\n")
        
        if voltage == "800V":
            f.write(f"\nComparison with Previous 800V (Old Detectors):\n")
            for det in range(1, 5):
                new_mpv = combined_mpvs.get(det, float('nan'))
                old_mpv = OLD_CALIBRATION[det]["mpv_mV"]
                new_sig = sigmas[det - 1]
                old_sig = OLD_JITTER[det]
                f.write(f"  Det {det}: MPV {old_mpv:.1f} → {new_mpv:.1f} mV "
                        f"({new_mpv - old_mpv:+.1f}), "
                        f"σ {old_sig:.4f} → {new_sig:.4f} ns "
                        f"({new_sig - old_sig:+.4f})\n")
    
    print(f"\nSaved: {results_path}")
    
    return {
        "voltage": voltage,
        "sigmas": sigmas,
        "mpvs": combined_mpvs,
        "pair_info": pair_info,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Stable Combined Analysis")
    parser.add_argument('--voltage', '-v', type=str, help='Voltage (e.g., 800V)')
    parser.add_argument('--all', '-a', action='store_true', help='All voltages')
    args = parser.parse_args()
    
    voltages = []
    if args.all:
        voltages = ["800V", "850V", "900V"]
    elif args.voltage:
        voltages = [args.voltage]
    else:
        parser.print_help()
        sys.exit(1)
    
    results = {}
    for v in voltages:
        r = analyze_combined(v)
        if r:
            results[v] = r
    
    return results


if __name__ == "__main__":
    main()
