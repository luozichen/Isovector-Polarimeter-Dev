import uproot
import awkward as ak
import numpy as np
import sys

def main():
    file_path = "../simulation/v0300_scattering/build/DET01_Scattering_Result.root"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    try:
        # Geant4 usually names the tree 'ntuple/1' or 'EventTree' or just the tree name.
        # Let's open it and find the tree.
        with uproot.open(file_path) as f:
            # Usually the first object is the tree
            tree_name = f.keys()[0]
            tree = f[tree_name]
            
            # The columns for Photoelectrons are indices 17 to 32.
            # However, uproot reads column names. 
            # In G4AnalysisManager, default names are 'E0', 'E1'... or just 'double_col_0'.
            # Let's just read the whole tree as an array.
            data = tree.arrays()
            
            # Since we know:
            # Cols 1-16: Edep
            # Cols 17-32: PE
            # The 30-degree ring detectors are indices 8 to 15.
            # L = 8 (0 deg), U = 10 (90 deg), R = 12 (180 deg), D = 14 (270 deg)
            
            # Assuming the columns are named sequentially, let's find the PE columns.
            keys = tree.keys()
            # PE columns start at index 17 in the Ntuple (1-based from Geant4's perspective)
            # In python (0-based keys array), the PE for detector 8 is at offset 1 + 16 + 8 = 25.
            # Let's just use the fact that detectors 8, 10, 12, 14 are L, U, R, D.
            
            # We count an event as a "hit" if Photoelectrons > 0
            # Let's find the exact column names for PE
            # Geant4 ntuple columns are usually named E0, E1, E2 ... or var1, var2...
            
            print(f"Opened {file_path}")
            
            # Let's grab the PE arrays. Geant4 default column names:
            # If not named, they might be 'int_0', 'int_1' or 'PE_0'. 
            # Let's try to match by index. The first column is EventID (int), then 16 doubles, then 16 ints (PE).
            
            int_keys = [k for k in keys if tree[k].typename == 'int32_t']
            if len(int_keys) >= 17:
                # EventID is int_keys[0]
                pe_keys = int_keys[1:17]
                
                L_hits = ak.sum(data[pe_keys[8]] > 0)
                U_hits = ak.sum(data[pe_keys[10]] > 0)
                R_hits = ak.sum(data[pe_keys[12]] > 0)
                D_hits = ak.sum(data[pe_keys[14]] > 0)
                
                print(f"Results for 30-degree Ring (1000 events):")
                print(f"N_L (0 deg)  : {L_hits}")
                print(f"N_U (90 deg) : {U_hits}")
                print(f"N_R (180 deg): {R_hits}")
                print(f"N_D (270 deg): {D_hits}")
                
                print("\nExpected Asymmetries:")
                if (L_hits + R_hits) > 0:
                    epsilon_LR = (L_hits - R_hits) / (L_hits + R_hits)
                    print(f"Left-Right Asymmetry (e_LR): {epsilon_LR:.3f}")
                
                if (L_hits + R_hits + U_hits + D_hits) > 0:
                    epsilon_T = ((L_hits + R_hits) - (U_hits + D_hits)) / (L_hits + R_hits + U_hits + D_hits)
                    print(f"Tensor Asymmetry (e_T)     : {epsilon_T:.3f}")
            else:
                print("Could not find the expected PE columns. Here are the keys:")
                print(keys)

    except Exception as e:
        print(f"Error reading ROOT file: {e}")

if __name__ == "__main__":
    main()
