import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import glob

# Add the parent directory to the path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.wfm import WfmReader

def plot_waveforms(data_dir, output_dir, voltage_str):
    """
    Reads .wfm files from data_dir and plots the first few waveforms.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # We want to specifically look at Detector 4 vs Detector 3 or 5
    # Let's find some files. The format is *_{XY}_Ch{Z}.wfm
    
    files = glob.glob(os.path.join(data_dir, '*.wfm'))
    
    # Let's group files by their prefix (everything before _Ch3.wfm or _Ch4.wfm)
    prefixes = set()
    for f in files:
        if '_Ch3.wfm' in f:
            prefixes.add(f.replace('_Ch3.wfm', ''))
        elif '_Ch4.wfm' in f:
            prefixes.add(f.replace('_Ch4.wfm', ''))
            
    # For each unique run, let's plot the first 5 waveforms
    for prefix in prefixes:
        # Ignore accidental repeat runs for this quick check
        if os.path.basename(prefix).startswith('r'):
            continue
            
        file_ch3 = prefix + '_Ch3.wfm'
        file_ch4 = prefix + '_Ch4.wfm'
        
        if not os.path.exists(file_ch3) or not os.path.exists(file_ch4):
            print(f"Skipping {prefix}, missing a channel.")
            continue
            
        # Parse the pair ID (e.g. 14, 54, 13)
        # The filename looks like 260507_212421_14
        basename = os.path.basename(prefix)
        parts = basename.split('_')
        if len(parts) >= 3:
            pair_id = parts[-1]
        else:
            pair_id = "unknown"
            
        try:
            reader3 = WfmReader(file_ch3)
            reader4 = WfmReader(file_ch4)
            
            t3, volts3 = reader3.read_data()
            t4, volts4 = reader4.read_data()
            
            # Convert to ns and mV
            t_ns = t3 * 1e9
            volts3_mv = volts3 * 1000
            volts4_mv = volts4 * 1000
            
            num_frames_to_plot = min(5, reader3.num_frames)
            
            fig, axs = plt.subplots(num_frames_to_plot, 1, figsize=(10, 2*num_frames_to_plot), sharex=True)
            if num_frames_to_plot == 1:
                axs = [axs]
                
            fig.suptitle(f"Cylindrical Stack: {pair_id} ({voltage_str}) - First {num_frames_to_plot} Events")
            
            det_top = pair_id[0] if len(pair_id) == 2 else "?"
            det_bot = pair_id[1] if len(pair_id) == 2 else "?"
            
            for i in range(num_frames_to_plot):
                axs[i].plot(t_ns, volts3_mv[i], label=f'Top: Det {det_top} (Ch3)', color='blue', alpha=0.8)
                axs[i].plot(t_ns, volts4_mv[i], label=f'Bottom: Det {det_bot} (Ch4)', color='red', alpha=0.8)
                axs[i].set_ylabel('Amplitude (mV)')
                axs[i].grid(True, linestyle='--', alpha=0.6)
                axs[i].legend(loc='upper right')
                
            axs[-1].set_xlabel('Time (ns)')
            plt.tight_layout()
            
            out_file = os.path.join(output_dir, f"waveforms_{pair_id}_{voltage_str}.png")
            plt.savefig(out_file, dpi=150)
            plt.close()
            print(f"Saved {out_file}")
            
        except Exception as e:
            print(f"Error processing {prefix}: {e}")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 800V Data
    data_800v = os.path.join(base_dir, 'data', 'LZC_800V_CYLINDRICAL')
    out_800v = os.path.join(base_dir, 'results', 'cylindrical', 'waveforms_800V')
    
    if os.path.exists(data_800v):
        print("Processing 800V data...")
        plot_waveforms(data_800v, out_800v, "800V")
        
    # 850V Data
    data_850v = os.path.join(base_dir, 'data', 'LZC_850V_CYLINDRICAL')
    out_850v = os.path.join(base_dir, 'results', 'cylindrical', 'waveforms_850V')
    
    if os.path.exists(data_850v):
        print("Processing 850V data...")
        plot_waveforms(data_850v, out_850v, "850V")
        
    print("\nDone! Check the results/cylindrical/ directory for the plots.")
