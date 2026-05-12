import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader
from analysis import config

def debug_baseline(data_dir):
    files = glob.glob(os.path.join(data_dir, '*_Ch1.wfm'))
    if not files:
        print("No files found.")
        return
        
    f = files[0]
    print(f"Checking file: {f}")
    
    reader = WfmReader(f)
    # Read with restoration
    t, v_corr = reader.read_data(baseline_restore=True)
    # Read without restoration
    _, v_raw = reader.read_data(baseline_restore=False)
    
    t_ns = t * 1e9
    
    event_idx = 0
    raw_pulse = v_raw[event_idx] * 1000 # mV
    corr_pulse = v_corr[event_idx] * 1000 # mV
    
    print(f"Raw Max: {np.max(raw_pulse):.2f} mV")
    print(f"Corr Max: {np.max(corr_pulse):.2f} mV")
    print(f"Noise Threshold: {config.POSITIVE_NOISE_THRESHOLD * 1000:.2f} mV")
    
    plt.figure(figsize=(10, 6))
    plt.plot(t_ns, raw_pulse, label='Raw', alpha=0.5)
    plt.plot(t_ns, corr_pulse, label='Corrected', alpha=0.8)
    plt.axhline(config.POSITIVE_NOISE_THRESHOLD * 1000, color='red', linestyle='--', label='Noise Threshold')
    plt.axhline(0, color='black', lw=1)
    plt.legend()
    plt.title(f"Baseline Restoration Debug: {os.path.basename(f)}")
    plt.xlabel("Time (ns)")
    plt.ylabel("Amplitude (mV)")
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "results", "baseline_debug.png")
    plt.savefig(out_path)
    print(f"Saved debug plot to {out_path}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, 'data', 'run_stable_800V')
    debug_baseline(data_dir)
