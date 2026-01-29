#!/usr/bin/env python3
"""
Compare Runs - Unified Comparison Script for Physical Detector Data

This script replaces the legacy compare_13_14.py and compare_15_16.py scripts.
It generates comparison plots between two runs with output that is IDENTICAL
to the legacy scripts to ensure backward compatibility.

Usage:
    python analysis/compare_runs.py --bg 15 --source 16 --channel 3
    python analysis/compare_runs.py --bg 13 --source 14 --channel 1 --bins 4
    
    # Legacy mode: generate exact filenames from old scripts
    python analysis/compare_runs.py --bg 15 --source 16 --channel 3 --legacy
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import sys
import glob

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import config
from analysis.utils.wfm import WfmReader
from analysis.utils import io


def load_single_channel(run_num: int, channel: int) -> tuple:
    """
    Load amplitude data for a single channel from a run.
    
    Args:
        run_num: Run number
        channel: Channel number to load
        
    Returns:
        Tuple of (amplitudes_mV, run_dir, num_events)
    """
    run_dir = io.find_run_dir(run_num)
    if not run_dir:
        raise ValueError(f"Run {run_num} not found in {config.DATA_DIR}")
    
    # Find WFM file for specified channel
    pattern = os.path.join(run_dir, f"*_Ch{channel}.wfm")
    wfm_files = glob.glob(pattern)
    
    if not wfm_files:
        raise ValueError(f"No Ch{channel} WFM file found in {run_dir}")
    
    wfm = WfmReader(wfm_files[0])
    _, v = wfm.read_data()
    
    # Calculate amplitudes (negative polarity -> take min and abs)
    amps = np.abs(np.min(v, axis=1)) * 1000  # Convert to mV
    
    return amps, run_dir, len(amps)


def plot_and_save(amps_bg, amps_th, bins, title, filename, 
                  label_bg, label_th, log_y=False, output_dir=None):
    """
    Plot comparison histogram - matches legacy script output exactly.
    """
    if output_dir is None:
        output_dir = config.RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(12, 7))
    
    plt.hist(amps_bg, bins=bins, histtype='step', linewidth=2, 
             color='royalblue', label=label_bg)
    
    plt.hist(amps_th, bins=bins, histtype='step', linewidth=2, 
             color='crimson', label=label_th)
    
    plt.title(title, fontsize=14)
    plt.xlabel("Peak Amplitude (mV)")
    plt.ylabel("Counts")
    
    if log_y:
        plt.yscale('log')
        plt.ylabel("Counts (Log Scale)")
        
    plt.legend()
    plt.grid(True, alpha=0.3, which="both")
    
    out_path = os.path.join(output_dir, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
    
    return out_path


def compare_13_14(output_dir=None):
    """
    Replicate exact output of legacy compare_13_14.py
    """
    print("Loading Run 013 (Background)...")
    amps_bg, _, n_bg = load_single_channel(13, 1)
    
    print("Loading Run 014 (Thorium)...")
    amps_th, _, n_th = load_single_channel(14, 1)
    
    # 1. Plot 0 to 100 mV (4mV bins - matches legacy)
    bins_100 = np.arange(0, 104, 4)
    plot_and_save(
        amps_bg, amps_th, bins_100,
        "Run 13 vs Run 14 Comparison (Single Fold Det 1) - 0 to 100 mV",
        "thorium_comparison_run13_14_0_100mV.png",
        f'Background (Run 13, N={n_bg})',
        f'Thorium (Run 14, N={n_th})',
        output_dir=output_dir
    )
    
    # 2. Plot Full Range (4mV bins)
    max_amp = max(np.max(amps_bg), np.max(amps_th))
    bins_full = np.arange(0, max_amp + 4, 4)
    plot_and_save(
        amps_bg, amps_th, bins_full,
        f"Run 13 vs Run 14 Comparison (Single Fold Det 1) - Full Range (0 to {max_amp:.0f} mV)",
        "thorium_comparison_run13_14_full_range.png",
        f'Background (Run 13, N={n_bg})',
        f'Thorium (Run 14, N={n_th})',
        output_dir=output_dir
    )


def compare_15_16(output_dir=None):
    """
    Replicate exact output of legacy compare_15_16.py
    """
    print("Loading Run 015 (Background)...")
    amps_bg, _, n_bg = load_single_channel(15, 3)
    
    print("Loading Run 016 (Thorium)...")
    amps_th, _, n_th = load_single_channel(16, 3)
    
    # 1. Plot 0 to 100 mV (2mV bins - matches legacy)
    bins_100 = np.arange(0, 102, 2)
    plot_and_save(
        amps_bg, amps_th, bins_100,
        "Run 15 vs Run 16 Comparison (Single Fold Det 3) - 0 to 100 mV",
        "thorium_comparison_run15_16_0_100mV.png",
        f'Background (Run 15, N={n_bg})',
        f'Thorium (Run 16, N={n_th})',
        output_dir=output_dir
    )
    
    # 2. Plot Full Range (Linear) (2mV bins)
    max_amp = max(np.max(amps_bg), np.max(amps_th))
    bins_full = np.arange(0, max_amp + 2, 2)
    plot_and_save(
        amps_bg, amps_th, bins_full,
        f"Run 15 vs Run 16 Comparison (Single Fold Det 3) - Full Range (0 to {max_amp:.0f} mV)",
        "thorium_comparison_run15_16_full_range.png",
        f'Background (Run 15, N={n_bg})',
        f'Thorium (Run 16, N={n_th})',
        output_dir=output_dir
    )
    
    # 3. Plot Full Range (Log Y)
    plot_and_save(
        amps_bg, amps_th, bins_full,
        f"Run 15 vs Run 16 Comparison (Single Fold Det 3) - Full Range (Log Scale)",
        "thorium_comparison_run15_16_full_range_log.png",
        f'Background (Run 15, N={n_bg})',
        f'Thorium (Run 16, N={n_th})',
        log_y=True,
        output_dir=output_dir
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compare amplitude distributions between two runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Legacy Presets (generates exact same output as old scripts):
    python compare_runs.py --preset 13-14    # Run 13 vs 14 (Det 1)
    python compare_runs.py --preset 15-16    # Run 15 vs 16 (Det 3)

Custom Comparison:
    python compare_runs.py --bg 15 --source 16 --channel 3 --bins 2
        """
    )
    parser.add_argument('--preset', type=str, choices=['13-14', '15-16'],
                        help='Use legacy preset for exact backward compatibility')
    parser.add_argument('--bg', type=int,
                        help='Background run number')
    parser.add_argument('--source', type=int,
                        help='Source run number')
    parser.add_argument('--channel', '-c', type=int,
                        help='Channel number to compare')
    parser.add_argument('--bins', '-b', type=float, default=2.0,
                        help='Bin width in mV (default: 2)')
    parser.add_argument('--output-dir', '-o', type=str, default=None,
                        help='Output directory (default: results/physical)')
    
    args = parser.parse_args()
    
    output_dir = args.output_dir or config.RESULTS_DIR
    
    # Handle legacy presets
    if args.preset == '13-14':
        compare_13_14(output_dir)
        return
    elif args.preset == '15-16':
        compare_15_16(output_dir)
        return
    
    # Custom comparison requires all arguments
    if not all([args.bg, args.source, args.channel]):
        parser.print_help()
        print("\nError: For custom comparison, --bg, --source, and --channel are required")
        sys.exit(1)
    
    # Load data
    print(f"Loading Run {args.bg:03d} (Background)...")
    try:
        amps_bg, dir_bg, n_bg = load_single_channel(args.bg, args.channel)
        print(f"  Loaded {n_bg} events from {dir_bg}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"Loading Run {args.source:03d} (Source)...")
    try:
        amps_source, dir_source, n_source = load_single_channel(args.source, args.channel)
        print(f"  Loaded {n_source} events from {dir_source}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Determine labels
    label_bg = f'Background (Run {args.bg}, N={n_bg})'
    label_source = f'Source (Run {args.source}, N={n_source})'
    
    # Check for thorium in dir name
    if 'thorium' in dir_source.lower():
        label_source = f'Thorium (Run {args.source}, N={n_source})'
    
    max_amp = max(np.max(amps_bg), np.max(amps_source))
    bin_width = args.bins
    channel_label = f"Det {args.channel}"
    
    print(f"\nGenerating comparison plots for {channel_label}...")
    
    # 1. 0 to 100 mV
    bins_100 = np.arange(0, 102, bin_width)
    plot_and_save(
        amps_bg, amps_source, bins_100,
        f"Run {args.bg} vs Run {args.source} Comparison (Single Fold {channel_label}) - 0 to 100 mV",
        f"thorium_comparison_run{args.bg}_{args.source}_0_100mV.png",
        label_bg, label_source,
        output_dir=output_dir
    )
    
    # 2. Full Range (Linear)
    bins_full = np.arange(0, max_amp + bin_width, bin_width)
    plot_and_save(
        amps_bg, amps_source, bins_full,
        f"Run {args.bg} vs Run {args.source} Comparison (Single Fold {channel_label}) - Full Range (0 to {max_amp:.0f} mV)",
        f"thorium_comparison_run{args.bg}_{args.source}_full_range.png",
        label_bg, label_source,
        output_dir=output_dir
    )
    
    # 3. Full Range (Log)
    plot_and_save(
        amps_bg, amps_source, bins_full,
        f"Run {args.bg} vs Run {args.source} Comparison (Single Fold {channel_label}) - Full Range (Log Scale)",
        f"thorium_comparison_run{args.bg}_{args.source}_full_range_log.png",
        label_bg, label_source,
        log_y=True,
        output_dir=output_dir
    )
    
    print("\nComparison complete!")


if __name__ == "__main__":
    main()
