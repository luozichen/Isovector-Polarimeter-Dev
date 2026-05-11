import sys
try:
    import ROOT
except ImportError:
    print("Please source ROOT")
    sys.exit(1)

def main():
    file_path = "simulation/v0200_coincidence/build/DET01_Cosmic_Result_long.root"
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        print(f"Error opening {file_path}")
        return

    tree = f.Get("CoincidenceData")
    if not tree:
        print("Error finding tree")
        return

    # In v0200, the variables were usually named "Time_PMT0", "Time_PMT1", etc.
    # We will draw the histogram of Time_PMT0 for events that had a hit
    
    # We only want events that actually deposited good energy (e.g. > 5 MeV) to mimic a real hit
    condition = "Edep_Scin0 > 5.0"
    
    tree.Draw("Time_PMT0>>hTime0", condition, "goff")
    hTime0 = ROOT.gDirectory.Get("hTime0")
    
    if hTime0:
        std_dev = hTime0.GetStdDev()
        print(f"Optical Jitter (Std Dev of hit times) for Det 0: {std_dev:.4f} ns")
    else:
        print("Could not create histogram.")

if __name__ == "__main__":
    main()
