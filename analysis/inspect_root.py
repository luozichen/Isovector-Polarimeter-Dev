import uproot
import sys

try:
    with uproot.open("simulation/v0200_coincidence/build/DET01_Cosmic_Result.root") as file:
        print("Keys in file:", file.keys())
        for key in file.keys():
            obj = file[key]
            if isinstance(obj, uproot.behaviors.TTree.TTree):
                print(f"Tree: {key}")
                print("Branches:", obj.keys())
except Exception as e:
    print(e)
