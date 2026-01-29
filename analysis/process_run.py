#!/usr/bin/env python3
"""
Process Run - Unified Analysis Script for Physical Detector Data

This is the main analysis script that replaces the legacy analyse_physical.py.
It uses the modular utils library for consistent, maintainable analysis.

Usage:
    python analysis/process_run.py 17
    python analysis/process_run.py --run 17
    python analysis/process_run.py --all
"""

import numpy as np
import argparse
import os
import sys
from scipy.optimize import lsq_linear

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import config
from analysis.utils import io, physics, plotting


def calculate_amplitudes(data: dict) -> dict:
    """
    Calculate peak amplitudes for all channels.
    
    Args:
        data: Dict mapping channel number to waveform matrices
        
    Returns:
        Dict mapping channel number to amplitude arrays (absolute values)
    """
    return {ch: np.abs(np.min(data[ch], axis=1)) for ch in data}


def calculate_cuts(amplitudes: dict, config_str: str) -> dict:
    """
    Calculate amplitude cuts for each channel based on detector position.
    
    Software Collimation Algorithm:
    - Top/Bottom detectors: 90% of Landau peak (to remove corner-clipped events)
    - Middle detectors: Only 50 mV floor (energy deposition skewed upward for angled tracks)
    
    Args:
        amplitudes: Dict mapping channel number to amplitude arrays
        config_str: Stack configuration string (e.g., "1234")
        
    Returns:
        Dict mapping channel number to cut values (in Volts)
    """
    cuts = {}
    
    # Identify detector positions in the stack
    # Position 0 = Top, Position 3 = Bottom, Positions 1&2 = Middle
    for ch, amps in amplitudes.items():
        # Find this detector's position in the stack
        det_char = str(ch)
        if det_char in config_str:
            position = config_str.index(det_char)
        else:
            position = -1  # Unknown
        
        # Calculate Landau peak
        counts, bins = np.histogram(amps, bins=100, range=(0, 0.5))
        bin_centers = (bins[:-1] + bins[1:]) / 2
        peak_idx = np.argmax(counts)
        peak_val = bin_centers[peak_idx]
        
        # Apply position-dependent cut logic
        if position == 0 or position == 3:
            # Top or Bottom detector: Apply 90% of Landau peak cut
            cut_val = max(config.DEFAULT_CUT_THRESHOLD_MV / 1000.0, peak_val * 0.9)
        else:
            # Middle detectors (pos 1 or 2) or unknown: Only use floor cut
            # Middle detectors see longer path lengths for angled tracks
            cut_val = config.DEFAULT_CUT_THRESHOLD_MV / 1000.0
        
        cuts[ch] = cut_val
    
    return cuts



def categorize_events(data: dict, amplitudes: dict, cuts: dict, num_events: int) -> tuple:
    """
    Categorize events into clean, clipped, and noise.
    
    Args:
        data: Dict mapping channel to waveform matrices
        amplitudes: Dict mapping channel to amplitude arrays
        cuts: Dict mapping channel to cut values
        num_events: Total number of events
        
    Returns:
        Tuple of (clean_indices, clipped_indices, noise_indices)
    """
    clean_indices = []
    clipped_indices = []
    noise_indices = []
    
    for i in range(num_events):
        # 1. Check Electronic Noise (Positive Excursion)
        is_electronic_noise = False
        for ch in data:
            if np.max(data[ch][i]) > config.POSITIVE_NOISE_THRESHOLD:
                is_electronic_noise = True
                break
        
        if is_electronic_noise:
            noise_indices.append(i)
            continue
            
        # 2. Check Clipping (Low Amplitude)
        is_clipped = False
        for ch in data:
            if amplitudes[ch][i] < cuts[ch]:
                is_clipped = True
                break
                
        if is_clipped:
            clipped_indices.append(i)
        else:
            clean_indices.append(i)
            
    return clean_indices, clipped_indices, noise_indices


def extract_timings(time: np.ndarray, data: dict, indices: list) -> dict:
    """
    Extract dCFD timings for specified events.
    
    Args:
        time: Time array
        data: Dict mapping channel to waveform matrices
        indices: Event indices to process
        
    Returns:
        Dict mapping channel to timing arrays
    """
    times = {ch: [] for ch in data}
    
    for idx in indices:
        for ch in data:
            t = physics.get_dcfd_time(time, data[ch][idx], config.CFD_FRACTION)
            times[ch].append(t)
            
    return {ch: np.array(times[ch]) for ch in times}


def solve_jitter(pair_vars: list) -> np.ndarray:
    """
    Solve for individual detector jitters from pair variances.
    
    Args:
        pair_vars: List of 6 pair variances in order (1-2, 1-3, 1-4, 2-3, 2-4, 3-4)
        
    Returns:
        Array of 4 individual detector sigmas
    """
    A = np.array([
        [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1], 
        [0, 1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 1]
    ])
    y = np.array(pair_vars)
    
    # Filter out NaN values
    valid_mask = ~np.isnan(y)
    if np.sum(valid_mask) < 4:
        return np.full(4, np.nan)
    
    res = lsq_linear(A[valid_mask], y[valid_mask], bounds=(0, np.inf))
    return np.sqrt(res.x)


def save_results(
    run_id: str,
    config_str: str,
    num_events: int,
    clean_count: int,
    clipped_count: int,
    noise_count: int,
    sigmas: np.ndarray,
    output_dir: str
):
    """Save analysis results to text file."""
    out_path = os.path.join(output_dir, f"{run_id}_jitter_results.txt")
    
    with open(out_path, "w") as f:
        f.write(f"Run: {run_id}\n")
        f.write(f"Config: {config_str}\n")
        f.write(f"Events: {num_events}\n")
        f.write(f"  Clean: {clean_count}\n")
        f.write(f"  Clipped: {clipped_count}\n")
        f.write(f"  Noise: {noise_count}\n")
        f.write("Jitter Results (sigma):\n")
        for i, s in enumerate(sigmas):
            det_id = i + 1
            pos_label = plotting.get_position_label(det_id, config_str)
            f.write(f"  Det {det_id} (Ch{det_id}) [{pos_label}]: {s:.4f} ns\n")
    
    print(f"  Saved results: {out_path}")


def analyze_run(run_num: int):
    """
    Main analysis function for a single run.
    
    Args:
        run_num: Run number to analyze
    """
    # Get run parameters
    params = config.get_run_params(run_num)
    landau_range = (params.landau_lower, params.landau_upper)
    
    # Load data
    try:
        time, data, meta = io.load_run_data(run_num)
    except ValueError as e:
        print(f"  Error: {e}")
        return
    
    if not data:
        print(f"  Skipping run {run_num}: No data files found")
        return
    
    run_id = meta.run_id
    config_str = meta.config
    
    print(f"\nAnalyzing: {run_id}")
    print(f"  Type: {params.run_type}")
    print(f"  Range: {params.landau_lower}-{params.landau_upper}V, Bins: {params.landau_bins}")
    if params.notes:
        print(f"  Notes: {params.notes}")
    
    # Determine number of channels
    channels = sorted(data.keys())
    num_channels = len(channels)
    num_events = data[channels[0]].shape[0]
    
    print(f"  Channels: {num_channels} ({channels})")
    print(f"  Events: {num_events}")
    
    # Calculate amplitudes
    amplitudes = calculate_amplitudes(data)
    
    # Create output directory
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    
    # Handle single detector runs differently
    if num_channels == 1:
        print("  Single detector run - plotting amplitude distribution only")
        
        ch = channels[0]
        # Simple histogram plot
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        amps_mV = amplitudes[ch] * 1000
        plt.hist(amps_mV, bins=params.landau_bins, 
                 range=(params.landau_lower*1000, params.landau_upper*1000),
                 histtype='stepfilled', alpha=0.6)
        plt.xlabel("Peak Amplitude (mV)")
        plt.ylabel("Counts")
        plt.title(f"{run_id} - Single Detector (Ch{ch}) Amplitude Distribution")
        plt.grid(True, alpha=0.3)
        
        out_path = os.path.join(config.RESULTS_DIR, f"{run_id}_amplitude_dist.png")
        plt.savefig(out_path, dpi=config.DEFAULT_DPI)
        plt.close()
        print(f"  Saved: {out_path}")
        return
    
    # 4-fold coincidence analysis
    if num_channels < 4:
        print(f"  Warning: Only {num_channels} channels found, expected 4 for full analysis")
    
    # Calculate cuts
    cuts = calculate_cuts(amplitudes, config_str)
    
    # Categorize events
    clean_indices, clipped_indices, noise_indices = categorize_events(
        data, amplitudes, cuts, num_events
    )
    
    print(f"  Clean: {len(clean_indices)} ({len(clean_indices)/num_events:.1%})")
    print(f"  Clipped (Low Energy): {len(clipped_indices)}")
    print(f"  Electronic Noise: {len(noise_indices)}")
    
    # Filter amplitudes for valid events
    valid_indices = sorted(clean_indices + clipped_indices)
    amplitudes_valid = {ch: amplitudes[ch][valid_indices] for ch in amplitudes}
    
    # Plot Landau fits
    plotting.plot_landau_fits(
        amplitudes_valid, cuts, run_id, config_str,
        landau_range, params.landau_bins
    )
    
    # Plot sample waveforms
    if clean_indices:
        plotting.plot_waveforms(time, data, clean_indices, run_id, 
                                "Good Waveforms", "good_waveforms")
    
    if clipped_indices:
        plotting.plot_waveforms(time, data, clipped_indices, run_id,
                                "Clipped / Low Energy Events", "clipped_check")
        
    if noise_indices:
        plotting.plot_waveforms(time, data, noise_indices, run_id,
                                "Electronic Noise (>30mV Positive)", "noise_check")
    
    # Jitter analysis requires sufficient clean events
    if len(clean_indices) < 10:
        print("  Not enough clean events for jitter analysis.")
        return
    
    # Extract timings
    print("  Extracting timings...")
    times = extract_timings(time, data, clean_indices)
    
    # Plot timing pairs and get variances
    _, pair_vars = plotting.plot_timing_pairs(times, run_id, config_str)
    
    # Solve for individual jitters
    sigmas = solve_jitter(pair_vars)
    
    # Print jitter results
    print("  Jitter Results (σ):")
    for i, s in enumerate(sigmas):
        det_id = i + 1
        pos_label = plotting.get_position_label(det_id, config_str)
        print(f"    Det {det_id} [{pos_label}]: {s:.4f} ns")
    
    # Save results
    save_results(
        run_id, config_str, num_events,
        len(clean_indices), len(clipped_indices), len(noise_indices),
        sigmas, config.RESULTS_DIR
    )


def main():
    parser = argparse.ArgumentParser(
        description="Process physical detector run data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python process_run.py 17           # Analyze run 17
    python process_run.py --run 17     # Same as above
    python process_run.py --all        # Analyze all runs
    python process_run.py 2 3 4 5      # Analyze runs 2, 3, 4, 5
        """
    )
    parser.add_argument('runs', nargs='*', type=int, 
                        help='Run number(s) to analyze')
    parser.add_argument('--run', '-r', type=int, 
                        help='Single run number to analyze')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Analyze all available runs')
    
    args = parser.parse_args()
    
    # Determine which runs to process
    runs_to_process = []
    
    if args.all:
        # Find all run directories
        import glob
        pattern = os.path.join(config.DATA_DIR, "run*")
        run_dirs = sorted(glob.glob(pattern))
        for run_dir in run_dirs:
            if os.path.isdir(run_dir):
                basename = os.path.basename(run_dir)
                import re
                match = re.search(r'run(\d+)', basename)
                if match:
                    runs_to_process.append(int(match.group(1)))
    elif args.run:
        runs_to_process = [args.run]
    elif args.runs:
        runs_to_process = args.runs
    else:
        parser.print_help()
        sys.exit(1)
    
    print(f"Processing runs: {runs_to_process}")
    
    for run_num in runs_to_process:
        try:
            analyze_run(run_num)
        except Exception as e:
            print(f"  Error processing run {run_num}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
