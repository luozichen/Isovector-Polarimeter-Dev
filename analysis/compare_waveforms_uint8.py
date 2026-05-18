#!/usr/bin/env python3
"""
Signed vs Unsigned Waveform Comparison

Loads waveforms using signed 'int8' and unsigned 'uint8' and compares their
peak amplitudes to see if there is any major discrepancy or incorrect peak extraction.
"""

import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

class UnsignedWfmReader(WfmReader):
    """ Override read_data to use uint8 instead of int8. """
    def read_data(self, baseline_restore=True):
        with open(self.filepath, 'rb') as f:
            f.seek(self.curve_offset)
            total_points = self.num_frames * self.time_size
            
            # Read as uint8 for format 7
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

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    f_900 = os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL', '260512_195730_15_Ch3.wfm')
    
    reader_signed = WfmReader(f_900)
    reader_unsigned = UnsignedWfmReader(f_900)
    
    t_s, volts_s = reader_signed.read_data(baseline_restore=True)
    t_u, volts_u = reader_unsigned.read_data(baseline_restore=True)
    
    amps_s = np.abs(np.min(volts_s, axis=1)) * 1000.0
    amps_u = np.abs(np.min(volts_u, axis=1)) * 1000.0
    
    diff = np.abs(amps_s - amps_u)
    max_diff_idx = np.argmax(diff)
    
    print(f"Comparison for: {os.path.basename(f_900)}")
    print(f"  Number of waveforms: {volts_s.shape[0]}")
    print(f"  Max amplitude difference: {diff[max_diff_idx]:.6f} mV (at Event {max_diff_idx})")
    print(f"  Event {max_diff_idx} Signed Peak Amp:   {amps_s[max_diff_idx]:.2f} mV")
    print(f"  Event {max_diff_idx} Unsigned Peak Amp: {amps_u[max_diff_idx]:.2f} mV")
    
    # Check if there are any events with difference > 0.1 mV
    num_diff = np.sum(diff > 0.1)
    print(f"  Number of waveforms with difference > 0.1 mV: {num_diff}")
    
    if num_diff > 0:
        diff_indices = np.where(diff > 0.1)[0]
        print(f"  First 5 different events' indices: {diff_indices[:5]}")
        for idx in diff_indices[:5]:
            print(f"    Event {idx}: Signed = {amps_s[idx]:.2f} mV, Unsigned = {amps_u[idx]:.2f} mV")

if __name__ == "__main__":
    main()
