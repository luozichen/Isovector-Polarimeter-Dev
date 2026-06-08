#!/usr/bin/env python3
"""
Unsigned uint8 Characterization Test

Runs the full cylindrical characterization at 800V, 850V, and 900V
but reads the 8-bit curves as unsigned 'np.uint8' instead of signed 'np.int8'
to see if the anomalous double-peak distributions vanish and reveal the true physics!
"""

import os
import sys
import numpy as np
import glob
from scipy.optimize import curve_fit, lsq_linear

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader
from analysis import config
from analysis.utils.physics import landau_fit_func, get_dcfd_time, gaussian

SIM_REF_MPV_MEV = 1.69

class UnsignedWfmReader(WfmReader):
    """ Override read_data to use uint8 instead of int8. """
    def read_data(self, baseline_restore=True) -> tuple[np.ndarray, np.ndarray]:
        with open(self.filepath, 'rb') as f:
            f.seek(self.curve_offset)
            total_points = self.num_frames * self.time_size
            
            # Read as uint8 for format 7
            if self.data_format == 7:
                raw_data = np.fromfile(f, dtype=np.uint8, count=total_points)
            else:
                return super().read_data(baseline_restore)
                
            # Reshape
            if raw_data.size != total_points:
                 frames_read = raw_data.size // self.time_size
                 if frames_read == 0:
                     raise ValueError(f"File {self.filepath} is too short.")
                 raw_data = raw_data[:frames_read * self.time_size]
                 frames = raw_data.reshape((frames_read, self.time_size))
            else:
                 frames = raw_data.reshape((self.num_frames, self.time_size))
            
            # Convert to Volts
            volts = frames.astype(np.float64) * self.volt_scale + self.volt_offset
            t = np.arange(self.time_size, dtype=np.float64) * self.time_scale + self.time_offset
            
            if baseline_restore:
                idx_base = min(len(t), 50)
                global_baseline_val = np.mean(volts[:, :idx_base])
                volts = volts - global_baseline_val
                
            return t, volts

def fit_landau_mpv(data: np.ndarray, bins: int = 100, range_val = (10, 450)) -> tuple:
    counts, bin_edges = np.histogram(data, bins=bins, range=range_val, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    max_idx = np.argmax(counts)
    mpv_est = bin_centers[max_idx]
    width_est = np.std(data) * 0.2
    amp_est = np.max(counts) * width_est * 3.0
    try:
        popt, _ = curve_fit(landau_fit_func, bin_centers, counts,
                           p0=[mpv_est, width_est, amp_est],
                           bounds=([10.0, 1.0, 0.0], [450.0, 150.0, np.inf]),
                           maxfev=10000)
        return popt[0], popt
    except:
        return mpv_est, None

def analyze_voltage(voltage_str: str, data_dir: str):
    print(f"\n=======================================================")
    print(f"  ANALYZING WITH UNSIGNED UINT8 READER AT {voltage_str}")
    print(f"=======================================================")
    
    if not os.path.exists(data_dir):
        return
        
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    detectors = [1, 3, 5, 6]
    det_amplitudes = {d: [] for d in detectors}
    
    for prefix in sorted(prefixes):
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            continue
            
        pair_id = os.path.basename(prefix).split('_')[-1]
        if len(pair_id) != 2:
            continue
            
        det_top = int(pair_id[0])
        det_bot = int(pair_id[1])
        
        if det_top == 4 or det_bot == 4:
            continue
            
        try:
            reader3 = UnsignedWfmReader(file_ch3)
            reader4 = UnsignedWfmReader(file_ch4)
            
            _, volts3 = reader3.read_data(baseline_restore=True)
            _, volts4 = reader4.read_data(baseline_restore=True)
            
            for i in range(volts3.shape[0]):
                if np.max(volts3[i]) > config.POSITIVE_NOISE_THRESHOLD or np.max(volts4[i]) > config.POSITIVE_NOISE_THRESHOLD:
                    continue
                    
                amp3_mV = np.abs(np.min(volts3[i])) * 1000.0
                amp4_mV = np.abs(np.min(volts4[i])) * 1000.0
                
                if amp3_mV < 10.0 or amp4_mV < 10.0:
                    continue
                    
                if det_top in det_amplitudes:
                    det_amplitudes[det_top].append(amp3_mV)
                if det_bot in det_amplitudes:
                    det_amplitudes[det_bot].append(amp4_mV)
                    
        except Exception as e:
            pass
            
    for d in detectors:
        amps = np.array(det_amplitudes[d])
        if len(amps) < 10:
            continue
        mpv, _ = fit_landau_mpv(amps, bins=100, range_val=(10, 450))
        print(f"  Det {d}: Mean Amp = {np.mean(amps):.2f} mV, Fitted Landau MPV = {mpv:.2f} mV (events: {len(amps)})")

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    analyze_voltage("800V", os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL'))
    analyze_voltage("850V", os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL'))
    analyze_voltage("900V", os.path.join(base_dir, 'data', 'LZC_900V_CYLINDRICAL'))

if __name__ == "__main__":
    main()
