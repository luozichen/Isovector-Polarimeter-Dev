import numpy as np
import matplotlib.pyplot as plt
from wfm_reader import WfmReader
import os
import glob

# --- Config ---
RUN13_DIR = "data/run013_10000_det_1_discriminator_10mV"
RUN14_DIR = "data/run014_10000_det_1_thorium_discriminator_10mV"
OUTPUT_PATH = "results/physical/thorium_comparison_single_fold.png"

def get_amplitudes(run_dir):
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch1.wfm"))
    if not wfm_files:
        print(f"No WFM files found in {run_dir}")
        return None
    
    wfm = WfmReader(wfm_files[0])
    _, v = wfm.read_data()
    # v shape: (num_frames, time_size)
    # Negative polarity -> take min and abs
    amps = np.abs(np.min(v, axis=1)) * 1000  # Convert to mV
    return amps

def main():
    print("Loading Run 013 (Background)...")
    amps_13 = get_amplitudes(RUN13_DIR)
    
    print("Loading Run 014 (Thorium)...")
    amps_14 = get_amplitudes(RUN14_DIR)
    
    if amps_13 is None or amps_14 is None:
        return

    plt.figure(figsize=(12, 7))
    
    # Range: 0 to 100 mV to focus on the primary data region
    bins = np.linspace(0, 100, 201)
    
    plt.hist(amps_13, bins=bins, histtype='step', linewidth=2, 
             color='royalblue', label=f'Background (Run 13, N={len(amps_13)})')
    
    plt.hist(amps_14, bins=bins, histtype='step', linewidth=2, 
             color='crimson', label=f'Thorium (Run 14, N={len(amps_14)})')
    
    # Overlay filled for Thorium to make it stand out
    plt.hist(amps_14, bins=bins, histtype='stepfilled', alpha=0.2, color='crimson')

    plt.title("Energy Deposition Comparison (Single Fold Det 1)\nThorium Source vs Background (10mV Threshold)", fontsize=14)
    plt.xlabel("Peak Amplitude (mV)")
    plt.ylabel("Counts")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Zoom in on low energy region in an inset? 
    # Or just set a log scale option? Let's keep it linear first as requested.
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"Saved comparison plot to {OUTPUT_PATH}")
    
    # Also save a version with Log Scale
    plt.yscale('log')
    plt.title("Energy Deposition Comparison (Single Fold Det 1) - LOG SCALE")
    log_output = OUTPUT_PATH.replace(".png", "_log.png")
    plt.savefig(log_output, dpi=150)
    print(f"Saved log comparison plot to {log_output}")

if __name__ == "__main__":
    main()
