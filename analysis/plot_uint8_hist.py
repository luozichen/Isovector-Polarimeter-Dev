#!/usr/bin/env python3
"""
Histogram Comparison: int8 vs. uint8

Generates and saves a side-by-side histogram comparison of Detector 1's peak amplitudes
at 800V using the signed 'int8' reader vs. the unsigned 'uint8' reader to see if the
double-peak feature is a parsing artifact or a physical data feature.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

class UnsignedWfmReader(WfmReader):
    def read_data(self, baseline_restore=True) -> tuple[np.ndarray, np.ndarray]:
        with open(self.filepath, 'rb') as f:
            f.seek(self.curve_offset)
            total_points = self.num_frames * self.time_size
            if self.data_format == 7:
                raw_data = np.fromfile(f, dtype=np.uint8, count=total_points)
            else:
                return super().read_data(baseline_restore)
            frames = raw_data.reshape((self.num_frames, self.time_size))
            volts = frames.astype(np.float64) * self.volt_scale + self.volt_offset
            t = np.arange(self.time_size, dtype=np.float64) * self.time_scale + self.time_offset
            if baseline_restore:
                idx_base = min(len(t), 50)
                global_baseline_val = np.mean(volts[:, :idx_base])
                volts = volts - global_baseline_val
            return t, volts

def get_amps(filepath, use_unsigned=False):
    if use_unsigned:
        reader = UnsignedWfmReader(filepath)
    else:
        reader = WfmReader(filepath)
    t, volts = reader.read_data(baseline_restore=True)
    amps = np.abs(np.min(volts, axis=1)) * 1000.0
    return amps[amps >= 10.0]

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f_800 = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL', '260508_173743_13_Ch3.wfm')
    
    amps_signed = get_amps(f_800, use_unsigned=False)
    amps_unsigned = get_amps(f_800, use_unsigned=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].hist(amps_signed, bins=100, range=(10, 450), alpha=0.7, color='blue', edgecolor='blue')
    axes[0].set_title("Signed (int8) Reader")
    axes[0].set_xlabel("Peak Amplitude (mV)")
    axes[0].set_ylabel("Counts")
    axes[0].grid(True, linestyle='--')
    
    axes[1].hist(amps_unsigned, bins=100, range=(10, 450), alpha=0.7, color='green', edgecolor='green')
    axes[1].set_title("Unsigned (uint8) Reader")
    axes[1].set_xlabel("Peak Amplitude (mV)")
    axes[1].set_ylabel("Counts")
    axes[1].grid(True, linestyle='--')
    
    plt.tight_layout()
    out_file = os.path.join(base_dir, 'results', 'physical', 'cylindrical', 'reader_comparison.png')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    plt.savefig(out_file, dpi=150)
    plt.close()
    print(f"Saved comparison plot to: {out_file}")

if __name__ == "__main__":
    main()
