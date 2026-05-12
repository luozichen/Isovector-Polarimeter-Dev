#!/usr/bin/env python3
"""
Run Stable Per-Config Analysis

Analyses each detector stack configuration within a run_stable_{voltage}/ folder.
Produces Landau fits, timing pair distributions, and per-config jitter results.
Follows the same pipeline as process_run.py.

Usage:
    python analyse_stable.py --voltage 800V
    python analyse_stable.py --voltage 900V
    python analyse_stable.py --all
"""

import numpy as np
import argparse
import os
import sys
import glob
import re
from scipy.optimize import curve_fit, lsq_linear
import matplotlib.pyplot as plt

# Add project root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

from analysis import config
from analysis.utils.wfm import WfmReader
from analysis.utils.physics import get_dcfd_time, landau_fit_func, gaussian

# =============================================================================
# Configuration
# =============================================================================

RESULTS_BASE = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results_corrected")

# Voltage-specific Landau fit ranges
VOLTAGE_PARAMS = {
    "800V": {"landau_range": (0.01, 0.4), "bins": 50},
    "850V": {"landau_range": (0.05, 0.5), "bins": 50},
    "900V": {"landau_range": (0.10, 0.6), "bins": 50},
}

DETECTOR_COLORS = {
    1: '#E57373',  # Red
    2: '#64B5F6',  # Blue
    3: '#81C784',  # Green
    4: '#FFB74D',  # Orange
}
PAIR_COLORS = ['#5C6BC0', '#26A69A', '#AB47BC', '#EF5350', '#42A5F5', '#66BB6A']


# =============================================================================
# Data Loading
# =============================================================================

def discover_configs(voltage_dir: str) -> list:
    """
    Discover all unique stack configurations in a voltage directory.
    Files are named: YYMMDD_HHMMSS_CFGSTR_ChN.wfm
    Returns list of (timestamp_prefix, config_str) tuples.
    """
    wfm_files = glob.glob(os.path.join(voltage_dir, "*_Ch*.wfm"))
    configs = {}
    
    for f in wfm_files:
        basename = os.path.basename(f)
        # Parse: YYMMDD_HHMMSS_CFGSTR_ChN.wfm
        match = re.match(r'(\d{6}_\d{6})_(\d{4})_Ch(\d+)\.wfm', basename)
        if match:
            timestamp = match.group(1)
            cfg = match.group(2)
            key = f"{timestamp}_{cfg}"
            if key not in configs:
                configs[key] = (timestamp, cfg)
    
    # Sort by timestamp
    return sorted(configs.values(), key=lambda x: x[0])


def load_config_data(voltage_dir: str, timestamp: str, config_str: str):
    """
    Load all 4 channels for a specific configuration.
    Returns: (time_array, {ch: volt_matrix}, num_events)
    """
    data = {}
    time = None
    min_events = float('inf')
    
    for ch in range(1, 5):
        filepath = os.path.join(voltage_dir, f"{timestamp}_{config_str}_Ch{ch}.wfm")
        if not os.path.exists(filepath):
            print(f"  [Warning] Missing: {filepath}")
            return None, {}, 0
        
        wfm = WfmReader(filepath)
        t, v = wfm.read_data()
        
        if time is None:
            time = t
        
        data[ch] = v
        min_events = min(min_events, v.shape[0])
    
    # Truncate to common length
    for ch in data:
        data[ch] = data[ch][:min_events]
    
    return time, data, min_events


# =============================================================================
# Analysis Functions (same logic as process_run.py)
# =============================================================================

def calculate_amplitudes(data: dict) -> dict:
    """Peak amplitude (absolute value of minimum) for each channel."""
    return {ch: np.abs(np.min(data[ch], axis=1)) for ch in data}


def get_position_label(det_id: int, config_str: str) -> str:
    """Returns Top/Mid1/Mid2/Bot label for a detector in the given config."""
    det_char = str(det_id)
    if det_char not in config_str:
        return "?"
    idx = config_str.index(det_char)
    return ["Top", "Mid1", "Mid2", "Bot"][idx]


def calculate_cuts(amplitudes: dict, config_str: str) -> dict:
    """
    Position-dependent amplitude cuts (Type A Landau Cut).
    Top/Bot: 90% of Landau peak. Middle: 50 mV floor only.
    """
    cuts = {}
    for ch, amps in amplitudes.items():
        det_char = str(ch)
        position = config_str.index(det_char) if det_char in config_str else -1
        
        counts, bins = np.histogram(amps, bins=100, range=(0, 0.5))
        bin_centers = (bins[:-1] + bins[1:]) / 2
        peak_val = bin_centers[np.argmax(counts)]
        
        if position == 0 or position == 3:
            cuts[ch] = max(config.DEFAULT_CUT_THRESHOLD_MV / 1000.0, peak_val * 0.9)
        else:
            cuts[ch] = config.DEFAULT_CUT_THRESHOLD_MV / 1000.0
    
    return cuts


def categorize_events(data: dict, amplitudes: dict, cuts: dict, num_events: int):
    """Categorize events as clean, clipped, or noise."""
    clean, clipped, noise = [], [], []
    
    for i in range(num_events):
        # Electronic noise check (positive excursion > 30 mV)
        is_noise = any(np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD for ch in data)
        if is_noise:
            noise.append(i)
            continue
        
        # Amplitude cut
        is_clipped = any(amplitudes[ch][i] < cuts[ch] for ch in data)
        if is_clipped:
            clipped.append(i)
        else:
            clean.append(i)
    
    return clean, clipped, noise


def extract_timings(time: np.ndarray, data: dict, indices: list) -> dict:
    """Extract dCFD timings for specified events."""
    times = {ch: [] for ch in data}
    for idx in indices:
        for ch in data:
            t = get_dcfd_time(time, data[ch][idx], config.CFD_FRACTION)
            times[ch].append(t)
    return {ch: np.array(times[ch]) for ch in times}


def solve_jitter(pair_vars: list) -> np.ndarray:
    """Solve for individual detector jitters from 6 pair variances."""
    A = np.array([
        [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1],
        [0, 1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 1]
    ])
    y = np.array(pair_vars)
    valid = ~np.isnan(y)
    if np.sum(valid) < 4:
        return np.full(4, np.nan)
    res = lsq_linear(A[valid], y[valid], bounds=(0, np.inf))
    return np.sqrt(res.x)


# =============================================================================
# Plotting
# =============================================================================

def plot_landau_fits(amplitudes, cuts, label, config_str, landau_range, bins_count, output_dir):
    """Plot Landau fits for all 4 detectors."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    fig.suptitle(f"{label} (Config {config_str}) — Energy Deposition", fontsize=14, fontweight='bold')
    
    mpvs = {}
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes[i]
        vals = amplitudes[ch]
        color = DETECTOR_COLORS[ch]
        
        y, x, _ = ax.hist(vals, bins=bins_count, range=landau_range,
                          density=False, histtype='stepfilled', alpha=0.5,
                          color=color, edgecolor=color, linewidth=1.5, label='Data')
        bin_centers = (x[:-1] + x[1:]) / 2
        
        if len(vals) > 0 and np.max(y) > 0:
            peak_idx = np.argmax(y)
            
            mpv_guess = bin_centers[peak_idx]
            bin_width = bin_centers[1] - bin_centers[0]
            width_guess = bin_width * 2
            amp_guess = np.max(y) * width_guess * np.sqrt(2 * np.pi)
            try:
                popt, _ = curve_fit(
                    landau_fit_func, bin_centers, y,
                    p0=[mpv_guess, width_guess, amp_guess],
                    bounds=([0, 1e-4, 0], [max(2.0, landau_range[1] * 2), 1, np.inf]),
                    maxfev=10000
                )
                x_fine = np.linspace(landau_range[0], landau_range[1], 200)
                ax.plot(x_fine, landau_fit_func(x_fine, *popt), 'k-', lw=2,
                        label=f'Landau Fit\nMPV = {popt[0]*1000:.1f} mV')
                # Zoom in nicely around the fitted MPV
                ax.set_xlim(max(0, popt[0] - 0.08), min(landau_range[1], popt[0] + 0.18))
                
                mpvs[ch] = popt[0] * 1000  # mV
            except Exception as e:
                print(f"  [Warning] Ch{ch} fit failed: {e}")
        
        cut_val = cuts[ch]
        ax.axvline(cut_val, color='#424242', linestyle='--', lw=1.5,
                   label=f'Cut: {cut_val*1000:.1f} mV')
        
        pos_label = get_position_label(ch, config_str)
        ax.set_title(f"Ch{ch} — Det {ch} [{pos_label}]", fontweight='bold')
        ax.set_xlabel("Amplitude (V)")
        ax.set_ylabel("Counts")
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, f"{label}_landau_fits.png")
    plt.savefig(out_path, dpi=config.DEFAULT_DPI)
    plt.close(fig)
    print(f"  Saved: {out_path}")
    
    return mpvs


def plot_timing_pairs(times, label, config_str, output_dir):
    """Plot timing pair distributions and return pair variances."""
    pairs = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    fig.suptitle(f"{label} — Time Differences (Clean Events)", fontsize=14, fontweight='bold')
    
    pair_vars = []
    
    for i, (chA, chB) in enumerate(pairs):
        ax = axes[i]
        tA, tB = times[chA], times[chB]
        mask = (~np.isnan(tA)) & (~np.isnan(tB))
        delta_t = (tA[mask] - tB[mask]) * 1e9  # ns
        
        # Filter strictly to (-10, 10) ns to avoid outlier stretch
        plot_range = (-10, 10)
        dt_core = delta_t[(delta_t >= plot_range[0]) & (delta_t <= plot_range[1])]
        
        color = PAIR_COLORS[i]
        counts, bins, _ = ax.hist(dt_core, bins=40, range=plot_range, alpha=0.6, density=True,
                                   color=color, edgecolor=color, linewidth=1.5)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        sigma = np.std(dt_core)
        try:
            popt, _ = curve_fit(gaussian, bin_centers, counts,
                                p0=[np.max(counts), np.mean(dt_core), sigma], maxfev=5000)
            sigma = abs(popt[2])
            x_fine = np.linspace(bins[0], bins[-1], 100)
            ax.plot(x_fine, gaussian(x_fine, *popt), 'k-', lw=2, label='Gaussian Fit')
        except:
            pass
        
        pair_vars.append(sigma**2)
        ax.set_title(f"Det {chA} — Det {chB}\nσ = {sigma:.3f} ns", fontweight='bold')
        ax.set_xlabel("Δt (ns)")
        ax.set_ylabel("Probability Density")
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, f"{label}_timing_pairs.png")
    plt.savefig(out_path, dpi=config.DEFAULT_DPI)
    plt.close()
    print(f"  Saved: {out_path}")
    
    return pair_vars


# =============================================================================
# Main Analysis
# =============================================================================

def analyze_voltage(voltage: str):
    """Run full per-config analysis for a given voltage."""
    voltage_dir = os.path.join(config.DATA_DIR, f"run_stable_{voltage}")
    if not os.path.isdir(voltage_dir):
        print(f"Error: Directory not found: {voltage_dir}")
        return
    
    params = VOLTAGE_PARAMS.get(voltage, VOLTAGE_PARAMS["800V"])
    landau_range = params["landau_range"]
    bins_count = params["bins"]
    
    output_dir = os.path.join(RESULTS_BASE, voltage)
    os.makedirs(output_dir, exist_ok=True)
    
    configs = discover_configs(voltage_dir)
    print(f"\n{'='*60}")
    print(f"Run Stable Analysis: {voltage}")
    print(f"Found {len(configs)} configurations")
    print(f"Landau range: {landau_range}, bins: {bins_count}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}")
    
    all_results = []
    
    for timestamp, config_str in configs:
        label = f"{voltage}_{config_str}"
        print(f"\n--- Config {config_str} (timestamp: {timestamp}) ---")
        
        # Load data
        time_arr, data, num_events = load_config_data(voltage_dir, timestamp, config_str)
        if time_arr is None:
            print("  Skipping: data load failed")
            continue
        
        print(f"  Events: {num_events}")
        
        # Amplitudes
        amplitudes = calculate_amplitudes(data)
        
        # Cuts
        cuts = calculate_cuts(amplitudes, config_str)
        
        # Categorize
        clean, clipped, noise = categorize_events(data, amplitudes, cuts, num_events)
        print(f"  Clean: {len(clean)} ({len(clean)/num_events:.1%})")
        print(f"  Clipped: {len(clipped)} ({len(clipped)/num_events:.1%})")
        print(f"  Noise: {len(noise)} ({len(noise)/num_events:.1%})")
        
        # Filter amplitudes for Landau plot (clean + clipped, excluding noise)
        valid_indices = sorted(clean + clipped)
        amplitudes_valid = {ch: amplitudes[ch][valid_indices] for ch in amplitudes}
        
        # Landau fits
        mpvs = plot_landau_fits(amplitudes_valid, cuts, label, config_str,
                                landau_range, bins_count, output_dir)
        
        # Jitter analysis
        if len(clean) < 10:
            print("  Not enough clean events for jitter analysis")
            continue
        
        print("  Extracting timings...")
        times = extract_timings(time_arr, data, clean)
        pair_vars = plot_timing_pairs(times, label, config_str, output_dir)
        sigmas = solve_jitter(pair_vars)
        
        print("  Jitter (σ):")
        for i, s in enumerate(sigmas):
            det = i + 1
            pos = get_position_label(det, config_str)
            print(f"    Det {det} [{pos}]: {s:.4f} ns")
        
        all_results.append({
            "config": config_str,
            "timestamp": timestamp,
            "num_events": num_events,
            "clean": len(clean),
            "clipped": len(clipped),
            "noise": len(noise),
            "mpvs": mpvs,
            "sigmas": sigmas,
        })
    
    # Save summary
    summary_path = os.path.join(output_dir, f"{voltage}_summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"Run Stable Analysis Summary: {voltage}\n")
        f.write(f"{'='*60}\n\n")
        
        for r in all_results:
            f.write(f"Config: {r['config']} (timestamp: {r['timestamp']})\n")
            f.write(f"  Events: {r['num_events']} (Clean: {r['clean']}, "
                    f"Clipped: {r['clipped']}, Noise: {r['noise']})\n")
            
            if r['mpvs']:
                f.write("  MPVs (mV):\n")
                for ch, mpv in sorted(r['mpvs'].items()):
                    f.write(f"    Det {ch}: {mpv:.1f} mV\n")
            
            f.write("  Jitter (σ, ns):\n")
            for i, s in enumerate(r['sigmas']):
                det = i + 1
                pos = get_position_label(det, r['config'])
                f.write(f"    Det {det} [{pos}]: {s:.4f} ns\n")
            f.write("\n")
    
    print(f"\nSaved summary: {summary_path}")
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Run Stable Per-Config Analysis")
    parser.add_argument('--voltage', '-v', type=str, help='Voltage to analyze (e.g., 800V)')
    parser.add_argument('--all', '-a', action='store_true', help='Analyze all voltages')
    args = parser.parse_args()
    
    voltages = []
    if args.all:
        voltages = ["800V", "850V", "900V"]
    elif args.voltage:
        voltages = [args.voltage]
    else:
        parser.print_help()
        sys.exit(1)
    
    for v in voltages:
        analyze_voltage(v)


if __name__ == "__main__":
    main()
