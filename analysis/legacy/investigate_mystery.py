import numpy as np
import matplotlib.pyplot as plt
from wfm_reader import WfmReader
import os
import glob

# --- Config ---
RUN_DIR = "data/run011_1000_config_1342_thorium_discriminator_5mV"
OUTPUT_DIR = "results/physical/mystery_investigation"

def get_dcfd_time(time, waveform, fraction=0.3):
    # Find Peak (Negative)
    idx_peak = np.argmin(waveform)
    v_peak = waveform[idx_peak]
    if v_peak > -0.0005: return np.nan # Too small for timing
    
    v_target = fraction * v_peak
    search_region = waveform[:idx_peak]
    candidates = np.where(search_region > v_target)[0]
    if len(candidates) == 0: return np.nan
    i = candidates[-1]
    if i >= len(search_region) - 1: return np.nan
    t_i = time[i]
    t_next = time[i+1]
    v_i = waveform[i]
    v_next = waveform[i+1]
    slope = (v_next - v_i)
    if slope == 0: return t_i
    return t_i + (t_next - t_i) * (v_target - v_i) / slope

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Load Data
    wfm_files = {ch: glob.glob(os.path.join(RUN_DIR, f"*_Ch{ch}.wfm"))[0] for ch in range(1, 5)}
    data = {}
    time = None
    for ch in range(1, 5):
        wfm = WfmReader(wfm_files[ch])
        t, v = wfm.read_data()
        data[ch] = v
        if time is None: time = t
    
    # Truncate to match
    min_samples = min(time.shape[0], data[1].shape[0])
    time = time[:min_samples]
    for ch in range(1, 5):
        data[ch] = data[ch][:min_samples, :]

    num_events = data[1].shape[1]
    amplitudes = {ch: np.abs(np.min(data[ch], axis=0)) * 1000 for ch in range(1, 5)}

    # 2. Filter for the "2-3mV Peak" in Ch 1
    target_indices = [i for i in range(num_events) if 1.5 < amplitudes[1][i] < 3.5]
    print(f"Investigating {len(target_indices)} events in the 2-3mV peak of Channel 1.")

    if not target_indices: return

    # 3. Waveforms
    fig, axes = plt.subplots(min(5, len(target_indices)), 1, figsize=(10, 15), sharex=True)
    if len(target_indices) == 1: axes = [axes]
    
    for i, idx in enumerate(target_indices[:5]):
        ax = axes[i]
        for ch in range(1, 5):
            ax.plot(time*1e9, data[ch][:, idx]*1000, label=f"Ch{ch} ({amplitudes[ch][idx]:.1f}mV)")
        ax.set_title(f"Event {idx} (Ch1 in Mystery Peak)")
        ax.set_ylabel("mV")
        ax.grid(True, alpha=0.3)
        if i == 0: ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "peak_waveforms.png"))
    print("Saved peak_waveforms.png")

    # 4. Timing Correlation
    dt_12 = []
    for idx in target_indices:
        t1 = get_dcfd_time(time, data[1][:, idx])
        t2 = get_dcfd_time(time, data[2][:, idx])
        if not np.isnan(t1) and not np.isnan(t2):
            dt_12.append((t1 - t2)*1e9)

    plt.figure(figsize=(8, 6))
    counts, bins, _ = plt.hist(dt_12, bins=40, range=(-50, 50), color='forestgreen', alpha=0.7)
    print("\nTiming Histogram (Det1-Det2):")
    for i in range(len(counts)):
        if counts[i] > 0:
            print(f"  {bins[i]:5.1f} to {bins[i+1]:5.1f} ns: {int(counts[i])}")
    plt.title("Time Difference (Det1-Det2) for 2-3mV Peak Events")
    plt.xlabel("Delta T (ns)")
    plt.ylabel("Counts")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(OUTPUT_DIR, "peak_timing.png"))
    print("Saved peak_timing.png")

if __name__ == "__main__":
    main()
