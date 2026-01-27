import numpy as np
import matplotlib.pyplot as plt
from wfm_reader import WfmReader
import os
import glob

# --- Config ---
RUN13_DIR = "data/run013_10000_det_1_discriminator_10mV"
RUN14_DIR = "data/run014_10000_det_1_thorium_discriminator_10mV"
OUTPUT_DIR = "results/physical"

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

def plot_and_save(amps_bg, amps_th, bins, title, filename):
    plt.figure(figsize=(12, 7))
    
    plt.hist(amps_bg, bins=bins, histtype='step', linewidth=2, 
             color='royalblue', label=f'Background (Run 13, N={len(amps_bg)})')
    
    plt.hist(amps_th, bins=bins, histtype='step', linewidth=2, 
             color='crimson', label=f'Thorium (Run 14, N={len(amps_th)})')
    
    plt.title(title, fontsize=14)
    plt.xlabel("Peak Amplitude (mV)")
    plt.ylabel("Counts")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    out_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading Run 013 (Background)...")
    amps_13 = get_amplitudes(RUN13_DIR)
    
    print("Loading Run 014 (Thorium)...")
    amps_14 = get_amplitudes(RUN14_DIR)
    
    if amps_13 is None or amps_14 is None:
        return

    # 1. Plot 0 to 100 mV
    bins_100 = np.arange(0, 104, 4) # 4mV bin width
    plot_and_save(amps_13, amps_14, bins_100, 
                  "Energy Deposition Comparison (Single Fold Det 1) - 0 to 100 mV", 
                  "thorium_comparison_single_fold_0_100mV.png")

    # 2. Plot Full Range
    max_amp = max(np.max(amps_13), np.max(amps_14))
    bins_full = np.arange(0, max_amp + 4, 4) # 4mV bin width
    plot_and_save(amps_13, amps_14, bins_full, 
                  f"Energy Deposition Comparison (Single Fold Det 1) - Full Range (0 to {max_amp:.0f} mV)", 
                  "thorium_comparison_single_fold_full_range.png")

if __name__ == "__main__":
    main()