import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def plot_cuboid_waveforms(data_dir, output_dir):
    """
    Reads .wfm files from the stable cuboid data directory and plots the first few waveforms.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    
    # Group files by their prefix (everything before _Ch1.wfm, etc.)
    prefixes = set()
    for f in files:
        if '_Ch1.wfm' in f:
            prefixes.add(f.replace('_Ch1.wfm', ''))
            
    # For each unique run, let's plot the first 5 waveforms
    for prefix in prefixes:
        file_ch1 = prefix + '_Ch1.wfm'
        file_ch2 = prefix + '_Ch2.wfm'
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not all(os.path.exists(f) for f in [file_ch1, file_ch2, file_ch3, file_ch4]):
            print(f"Skipping {prefix}, missing a channel.")
            continue
            
        basename = os.path.basename(prefix)
        parts = basename.split('_')
        if len(parts) >= 3:
            config_id = parts[-1]
        else:
            config_id = "unknown"
            
        try:
            reader1 = WfmReader(file_ch1)
            reader2 = WfmReader(file_ch2)
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            
            t1, volts1 = reader1.read_data()
            _, volts2 = reader2.read_data()
            _, volts3 = reader3.read_data()
            _, volts4 = reader4.read_data()
            
            # Convert to ns and mV (NO BASELINE RESTORATION)
            t_ns = t1 * 1e9
            volts1_mv = volts1 * 1000
            volts2_mv = volts2 * 1000
            volts3_mv = volts3 * 1000
            volts4_mv = volts4 * 1000
            
            num_frames_to_plot = min(5, reader1.num_frames)
            
            fig, axs = plt.subplots(num_frames_to_plot, 1, figsize=(10, 2.5*num_frames_to_plot), sharex=True)
            if num_frames_to_plot == 1:
                axs = [axs]
                
            fig.suptitle(f"Cuboid Stack (Stable): Config {config_id} (800V) - First {num_frames_to_plot} Events")
            
            for i in range(num_frames_to_plot):
                axs[i].plot(t_ns, volts1_mv[i], label=f'Ch1 (Det {config_id[0]})', alpha=0.8)
                axs[i].plot(t_ns, volts2_mv[i], label=f'Ch2 (Det {config_id[1]})', alpha=0.8)
                axs[i].plot(t_ns, volts3_mv[i], label=f'Ch3 (Det {config_id[2]})', alpha=0.8)
                axs[i].plot(t_ns, volts4_mv[i], label=f'Ch4 (Det {config_id[3]})', alpha=0.8)
                axs[i].set_ylabel('Amplitude (mV)')
                axs[i].grid(True, linestyle='--', alpha=0.6)
                axs[i].legend(loc='upper right')
                
                # Add a thick black line at exactly 0 mV to make visual checking easy
                axs[i].axhline(0, color='black', linewidth=1.5, linestyle='-')
                
            axs[-1].set_xlabel('Time (ns)')
            plt.tight_layout()
            
            out_file = os.path.join(output_dir, f"waveforms_cuboid_{config_id}_800V.png")
            plt.savefig(out_file, dpi=150)
            plt.close()
            print(f"Saved {out_file}")
            
        except Exception as e:
            print(f"Error processing {prefix}: {e}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, 'data', 'run_stable_800V')
    output_dir = os.path.join(base_dir, 'results', 'physical', 'cuboid_waveforms')
    
    if os.path.exists(data_dir):
        print("Processing 800V stable cuboid data...")
        plot_cuboid_waveforms(data_dir, output_dir)
    else:
        print(f"Could not find data directory: {data_dir}")
        
    print("\nDone! Check the results/physical/cuboid_waveforms/ directory.")
