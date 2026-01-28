import numpy as np
import matplotlib.pyplot as plt
from wfm_reader import WfmReader
import os
import glob

# --- Config ---
RUN15_DIR = "data/run015_20000_det_3_discriminator_10mV"
RUN16_DIR = "data/run016_20000_det_3_thorium_discriminator_10mV"
OUTPUT_DIR = "results/physical"

def get_amplitudes(run_dir):
    # Note: Using Ch3 based on directory name
    wfm_files = glob.glob(os.path.join(run_dir, "*_Ch3.wfm"))
    if not wfm_files:
        print(f"No WFM files found in {run_dir}")
        return None
    
    wfm = WfmReader(wfm_files[0])
    _, v = wfm.read_data()
    # v shape: (num_frames, time_size)
    # Negative polarity -> take min and abs
    amps = np.abs(np.min(v, axis=1)) * 1000  # Convert to mV
    return amps

def plot_and_save(amps_bg, amps_th, bins, title, filename, log_y=False):
    plt.figure(figsize=(12, 7))
    
    plt.hist(amps_bg, bins=bins, histtype='step', linewidth=2, 
             color='royalblue', label=f'Background (Run 15, N={len(amps_bg)})')
    
    plt.hist(amps_th, bins=bins, histtype='step', linewidth=2, 
             color='crimson', label=f'Thorium (Run 16, N={len(amps_th)})')
    
    plt.title(title, fontsize=14)
    plt.xlabel("Peak Amplitude (mV)")
    plt.ylabel("Counts")
    
    if log_y:
        plt.yscale('log')
        plt.ylabel("Counts (Log Scale)")
        
    plt.legend()
    plt.grid(True, alpha=0.3, which="both")
    
    out_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading Run 015 (Background)...")
    amps_bg = get_amplitudes(RUN15_DIR)
    
    print("Loading Run 016 (Thorium)...")
    amps_th = get_amplitudes(RUN16_DIR)
    
    if amps_bg is None or amps_th is None:
        return

    # 1. Plot 0 to 100 mV (Linear)
    # Resolution check: 50mV/div -> approx 2mV per bit. 
    # We use 2mV bin width.
    bins_100 = np.arange(0, 102, 2) 
    plot_and_save(amps_bg, amps_th, bins_100, 
                  "Run 15 vs Run 16 Comparison (Single Fold Det 3) - 0 to 100 mV", 
                  "thorium_comparison_run15_16_0_100mV.png")

    # 2. Plot Full Range (Linear)
    max_amp = max(np.max(amps_bg), np.max(amps_th))
    bins_full = np.arange(0, max_amp + 2, 2) # 2mV bin width
    plot_and_save(amps_bg, amps_th, bins_full, 
                  f"Run 15 vs Run 16 Comparison (Single Fold Det 3) - Full Range (0 to {max_amp:.0f} mV)", 
                  "thorium_comparison_run15_16_full_range.png")

    # 3. Plot Full Range (Log Y)
    plot_and_save(amps_bg, amps_th, bins_full, 
                  f"Run 15 vs Run 16 Comparison (Single Fold Det 3) - Full Range (Log Scale)", 
                  "thorium_comparison_run15_16_full_range_log.png", log_y=True)

if __name__ == "__main__":
    main()
