import numpy as np
from wfm_reader import WfmReader
import os
import glob

RUN_DIR = "data/run011_1000_config_1342_thorium_discriminator_5mV"

def main():
    wfm_files = glob.glob(os.path.join(RUN_DIR, "*_Ch1.wfm"))
    if not wfm_files: return
    
    # Just read Ch1 to check its amplitude distribution
    wfm = WfmReader(wfm_files[0])
    _, v = wfm.read_data()
    
    # Calculate amplitudes (mV)
    # v shape: (samples, events)
    amps = np.abs(np.min(v, axis=0)) * 1000
    
    print("Channel 1 Amplitude Stats:")
    print(f"  Min: {np.min(amps):.2f} mV")
    print(f"  Max: {np.max(amps):.2f} mV")
    print(f"  Mean: {np.mean(amps):.2f} mV")
    
    # Histogram
    hist, bins = np.histogram(amps, bins=20, range=(0, 20))
    print("\nHistogram (0-20 mV):")
    for i in range(len(hist)):
        print(f"  {bins[i]:4.1f} - {bins[i+1]:4.1f} mV: {hist[i]}")

if __name__ == "__main__":
    main()


