import sys

try:
    import ROOT
except ImportError:
    print("Could not import ROOT. Please ensure your ROOT environment is sourced.")
    sys.exit(1)

def main():
    file_path = "simulation/v0300_scattering/build/DET01_Scattering_Result.root"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    # Open the ROOT file
    f = ROOT.TFile.Open(file_path)
    if not f or f.IsZombie():
        print(f"Error: Could not open {file_path}")
        return

    # Get the Ntuple (Tree)
    tree = f.Get("ScatteringData")
    if not tree:
        print("Error: Could not find tree 'ScatteringData'")
        return

    # In the 30-degree ring (Ring 1), the indices are 8 to 15.
    # L = 0 deg (Index 8)
    # U = 90 deg (Index 10)
    # R = 180 deg (Index 12)
    # D = 270 deg (Index 14)

    # We count an event if PE > 0
    L_hits = tree.GetEntries("PE_PMT8 > 0")
    U_hits = tree.GetEntries("PE_PMT10 > 0")
    R_hits = tree.GetEntries("PE_PMT12 > 0")
    D_hits = tree.GetEntries("PE_PMT14 > 0")

    print(f"\n--- Results for 30-degree Ring (1000 events) ---")
    print(f"N_L (0 deg)  : {L_hits}")
    print(f"N_U (90 deg) : {U_hits}")
    print(f"N_R (180 deg): {R_hits}")
    print(f"N_D (270 deg): {D_hits}")

    if (L_hits + R_hits) > 0:
        epsilon_LR = (L_hits - R_hits) / float(L_hits + R_hits)
        print(f"\nLeft-Right Asymmetry (e_LR): {epsilon_LR:.3f}")
        
    if (L_hits + R_hits + U_hits + D_hits) > 0:
        epsilon_T = ((L_hits + R_hits) - (U_hits + D_hits)) / float(L_hits + R_hits + U_hits + D_hits)
        print(f"Tensor Asymmetry (e_T)     : {epsilon_T:.3f}")

if __name__ == "__main__":
    main()
