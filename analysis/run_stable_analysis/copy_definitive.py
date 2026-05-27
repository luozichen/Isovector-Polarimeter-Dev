#!/usr/bin/env python3
"""
Copy and organize the definitive analysis results to results/definitive/
"""
import os
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(PROJECT_ROOT, "results", "physical", "run_stable_results_corrected")
DEST_DIR = os.path.join(PROJECT_ROOT, "results", "definitive")

def copy_file(src_path, dest_name):
    if os.path.exists(src_path):
        dest_path = os.path.join(DEST_DIR, dest_name)
        shutil.copy2(src_path, dest_path)
        print(f"Copied: {src_path} -> {dest_path}")
    else:
        print(f"[Warning] Source not found: {src_path}")

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # 1. Copy top-level plots
    copy_file(os.path.join(SRC_DIR, "voltage_comparison_corrected.png"), "gain_vs_voltage.png")
    copy_file(os.path.join(SRC_DIR, "thesis_jitter_comparison_curve.png"), "jitter_vs_voltage.png")
    
    # 2. Copy combined landau grid and golden jitter pairs plots for each voltage
    for v in ["800V", "850V", "900V"]:
        v_src_dir = os.path.join(SRC_DIR, v)
        
        # Landau Grid (default 50 bins)
        copy_file(os.path.join(v_src_dir, f"{v}_combined_landau_grid.png"), f"landau_grid_{v}.png")
        
        # Golden pairs timing jitter plot
        copy_file(os.path.join(v_src_dir, f"{v}_golden_pairs_jitter.png"), f"jitter_pairs_{v}.png")
        
        # Individual results text file
        copy_file(os.path.join(v_src_dir, f"{v}_combined_results.txt"), f"combined_results_{v}.txt")

    # 3. Create energy deposition and calibration summary
    energy_summary_path = os.path.join(DEST_DIR, "energy_deposition_summary.txt")
    with open(energy_summary_path, "w") as f:
        f.write("DEFINITIVE ENERGY DEPOSITION & CALIBRATION VALUES\n")
        f.write("=" * 60 + "\n")
        f.write("Reference Simulation Energy MPV (4-Fold): 30.01 MeV\n\n")
        
        f.write("Gain (Most Probable Value in mV):\n")
        f.write("-" * 60 + "\n")
        f.write("Detector |    800V    |    850V    |    900V    |\n")
        f.write("-" * 60 + "\n")
        f.write("  Det 1  |  252.1 mV  |  307.1 mV  |  367.9 mV  |\n")
        f.write("  Det 2  |  247.8 mV  |  290.2 mV  |  334.1 mV  |\n")
        f.write("  Det 3  |  241.2 mV  |  285.2 mV  |  333.6 mV  |\n")
        f.write("  Det 4  |  320.9 mV  |  380.9 mV  |  440.3 mV  |\n")
        f.write("-" * 60 + "\n")
        f.write(" Average |  265.5 mV  |  315.9 mV  |  369.0 mV  |\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("Calibration Constants (MeV/mV):\n")
        f.write("-" * 60 + "\n")
        f.write("Detector |    800V    |    850V    |    900V    |\n")
        f.write("-" * 60 + "\n")
        f.write("  Det 1  |   0.1190   |   0.0977   |   0.0816   |\n")
        f.write("  Det 2  |   0.1211   |   0.1034   |   0.0898   |\n")
        f.write("  Det 3  |   0.1244   |   0.1052   |   0.0900   |\n")
        f.write("  Det 4  |   0.0935   |   0.0788   |   0.0682   |\n")
        f.write("-" * 60 + "\n")
        f.write(" Average |   0.1145   |   0.0963   |   0.0824   |\n")
        f.write("=" * 60 + "\n")
        
    print(f"Created: {energy_summary_path}")

    # 4. Create intrinsic jitter summary
    jitter_summary_path = os.path.join(DEST_DIR, "intrinsic_jitter_summary.txt")
    with open(jitter_summary_path, "w") as f:
        f.write("DEFINITIVE INTRINSIC TIMING JITTER (σ) VALUES\n")
        f.write("=" * 65 + "\n")
        f.write("Extracted via Overdetermined Design Matrix Solver (Method 3)\n")
        f.write("Statistical uncertainties are approximately 15-20 ps (~3.2%)\n\n")
        
        f.write("Intrinsic Jitter (σ in ns):\n")
        f.write("-" * 65 + "\n")
        f.write("Detector |    800V    |    850V    |    900V    |   Old 800V  |\n")
        f.write("-" * 65 + "\n")
        f.write("  Det 1  | 0.5660  ns | 0.4482  ns | 0.4972  ns |  0.5050 ns  |\n")
        f.write("  Det 2  | 0.5375  ns | 0.5448  ns | 0.4952  ns |  0.5070 ns  |\n")
        f.write("  Det 3  | 0.6555  ns | 0.6454  ns | 0.5821  ns |  0.5410 ns  |\n")
        f.write("  Det 4  | 0.4735  ns | 0.5140  ns | 0.4932  ns |  0.5310 ns  |\n")
        f.write("-" * 65 + "\n")
        f.write(" Average | 0.5581  ns | 0.5381  ns | 0.5169  ns |  0.5210 ns  |\n")
        f.write("=" * 65 + "\n\n")
        
        f.write("Full Width at Half Maximum (FWHM = 2.355 * σ in ns):\n")
        f.write("-" * 65 + "\n")
        f.write("Detector |    800V    |    850V    |    900V    |   Old 800V  |\n")
        f.write("-" * 65 + "\n")
        f.write("  Det 1  | 1.3330  ns | 1.0555  ns | 1.1710  ns |  1.1893 ns  |\n")
        f.write("  Det 2  | 1.2659  ns | 1.2830  ns | 1.1663  ns |  1.1940 ns  |\n")
        f.write("  Det 3  | 1.5438  ns | 1.5199  ns | 1.3708  ns |  1.2741 ns  |\n")
        f.write("  Det 4  | 1.1150  ns | 1.2104  ns | 1.1616  ns |  1.2505 ns  |\n")
        f.write("-" * 65 + "\n")
        f.write(" Average | 1.3144  ns | 1.2672  ns | 1.2174  ns |  1.2269 ns  |\n")
        f.write("=" * 65 + "\n")

    print(f"Created: {jitter_summary_path}")
    print("\nDefinitive folder organization complete!")

if __name__ == "__main__":
    main()
