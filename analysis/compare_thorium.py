#!/usr/bin/env python3
"""
Compare Thorium - 4-Fold Coincidence Thorium vs Background Comparison

This script replaces the legacy compare_thorium_background.py.
It generates 2x2 grid comparison plots for 4-detector stacks with 
energy calibration applied.

Usage:
    python analysis/compare_thorium.py --preset 11-12      # 5mV threshold
    python analysis/compare_thorium.py --preset 9-10       # 15mV threshold  
    python analysis/compare_thorium.py --preset 7-8        # 50mV threshold
    python analysis/compare_thorium.py --bg 12 --source 11 # Custom
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


# Detector labels for the 4-detector grid
DETECTOR_LABELS = {
    1: "Det 1 (Top)",
    2: "Det 2 (Bot)",
    3: "Det 3 (Mid1)",
    4: "Det 4 (Mid2)"
}


def load_all_amplitudes(run_num: int) -> dict:
    """
    Load amplitude data for all 4 channels from a run.
    
    Returns:
        Dict mapping channel (1-4) to amplitude array (in Volts)
    """
    run_dir = io.find_run_dir(run_num)
    if not run_dir:
        raise ValueError(f"Run {run_num} not found in {config.DATA_DIR}")
    
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch*.wfm"))
    if not wfm_files:
        raise ValueError(f"No WFM files found in {run_dir}")
    
    # Group files by prefix
    sets = {}
    for f in wfm_files:
        basename = os.path.basename(f)
        parts = basename.split("_Ch")
        if len(parts) != 2:
            continue
        prefix = parts[0]
        ch = int(parts[1].split(".")[0])
        if prefix not in sets:
            sets[prefix] = {}
        sets[prefix][ch] = f
    
    if not sets:
        raise ValueError(f"Could not parse WFM files in {run_dir}")
    
    prefix = list(sets.keys())[0]
    file_map = sets[prefix]
    
    amplitudes = {}
    for ch in range(1, 5):
        if ch not in file_map:
            continue
        wfm = WfmReader(file_map[ch])
        _, v = wfm.read_data()
        # Amplitude in Volts (negative polarity -> take min and abs)
        amps = np.abs(np.min(v, axis=1))
        amplitudes[ch] = amps
    
    return amplitudes


def compare_thorium_4fold(
    bg_run: int,
    source_run: int,
    threshold_label: str,
    output_filename: str,
    output_dir: str = None
):
    """
    Generate 2x2 grid comparison plot for 4-fold thorium vs background.
    Matches legacy compare_thorium_background.py output exactly.
    """
    if output_dir is None:
        output_dir = config.RESULTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading Run {bg_run:03d} (Background)...")
    data_bg = load_all_amplitudes(bg_run)
    
    print(f"Loading Run {source_run:03d} (Thorium)...")
    data_th = load_all_amplitudes(source_run)
    
    if not data_bg or not data_th:
        print("Error: Could not load data for comparison.")
        return
    
    # --- Plotting ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    fig.suptitle(
        f"Thorium Source vs Cosmic Background ({threshold_label} Threshold)\n"
        f"(Run {source_run:03d} [Thorium] vs Run {bg_run:03d} [Background] - Stack 1342)",
        fontsize=16
    )
    
    for i, ch in enumerate(range(1, 5)):
        ax = axes[i]
        
        # Convert to MeV using calibration constants
        cal = config.CALIBRATION[ch]["mev_per_mV"]
        bg_mev = data_bg[ch] * 1000 * cal  # Volts -> mV -> MeV
        th_mev = data_th[ch] * 1000 * cal
        
        # Range: 0 to 60 MeV (covers Landau peak ~30 MeV and low energy)
        bins = np.linspace(0, 60, 61)
        
        # Plot Background (step)
        ax.hist(bg_mev, bins=bins, histtype='step', linewidth=2,
                color='royalblue', 
                label=f'Background (Run {bg_run}) (N={len(bg_mev)})',
                density=True)
        
        # Plot Thorium (filled + step outline)
        ax.hist(th_mev, bins=bins, histtype='stepfilled', alpha=0.3,
                color='crimson',
                label=f'Thorium (Run {source_run}) (N={len(th_mev)})',
                density=True)
        ax.hist(th_mev, bins=bins, histtype='step', linewidth=2,
                color='crimson', density=True)
        
        ax.set_title(DETECTOR_LABELS[ch])
        ax.set_xlabel("Energy Deposited (MeV)")
        ax.set_ylabel("Normalized Count Density")
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path = os.path.join(output_dir, output_filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved comparison plot to {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare 4-fold thorium vs background runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Legacy Presets (generates exact same output as old scripts):
    python compare_thorium.py --preset 11-12    # 5mV threshold
    python compare_thorium.py --preset 9-10     # 15mV threshold
    python compare_thorium.py --preset 7-8      # 50mV threshold

Custom Comparison:
    python compare_thorium.py --bg 12 --source 11 --label "5mV" --output "my_comparison.png"
        """
    )
    parser.add_argument('--preset', type=str, choices=['11-12', '9-10', '7-8'],
                        help='Use legacy preset for exact backward compatibility')
    parser.add_argument('--bg', type=int,
                        help='Background run number')
    parser.add_argument('--source', type=int,
                        help='Source (Thorium) run number')
    parser.add_argument('--label', type=str, default="",
                        help='Threshold label (e.g., "5mV", "15mV")')
    parser.add_argument('--output', type=str, default=None,
                        help='Output filename')
    parser.add_argument('--output-dir', '-o', type=str, default=None,
                        help='Output directory (default: results/physical)')
    
    args = parser.parse_args()
    
    output_dir = args.output_dir or config.RESULTS_DIR
    
    # Handle legacy presets
    if args.preset == '11-12':
        compare_thorium_4fold(12, 11, "5mV", "thorium_comparison_5mV.png", output_dir)
        return
    elif args.preset == '9-10':
        compare_thorium_4fold(10, 9, "15mV", "thorium_comparison_15mV.png", output_dir)
        return
    elif args.preset == '7-8':
        compare_thorium_4fold(7, 8, "50mV", "thorium_comparison_50mV.png", output_dir)
        return
    
    # Custom comparison
    if not all([args.bg, args.source]):
        parser.print_help()
        print("\nError: For custom comparison, --bg and --source are required")
        sys.exit(1)
    
    label = args.label or f"Run {args.bg} vs {args.source}"
    output = args.output or f"thorium_comparison_{args.bg}_{args.source}.png"
    
    compare_thorium_4fold(args.bg, args.source, label, output, output_dir)
    print("\nComparison complete!")


if __name__ == "__main__":
    main()
