// analyse_v0700_fom.C
// Figure of Merit analysis for the v0700 Cylindrical Digital Twin.
// Usage: root -l -q analysis/analyse_v0700_fom.C
//   (Run from the repository root directory)

void analyse_v0700_fom() {
    TFile *f = TFile::Open("simulation/v0700_cylindrical_twin/build/DET01_Scattering_Result.root");
    if (!f || f->IsZombie()) {
        cout << "Error opening file!" << endl;
        return;
    }

    TTree *tree = (TTree*)f->Get("ScatteringData");
    if (!tree) {
        cout << "Error finding tree!" << endl;
        return;
    }

    // Count hits for each detector that pass the 10 MeV threshold
    // Ring 0 (20 degrees): 0 (Left), 1 (Up), 2 (Right), 3 (Down)
    // Ring 1 (30 degrees): 4 (Left), 5 (Up), 6 (Right), 7 (Down)
    
    int counts[8] = {0};
    double edep[8];
    for (int i=0; i<8; i++) {
        tree->SetBranchAddress(Form("Edep_Scin%d", i), &edep[i]);
    }
    
    int nEvents = tree->GetEntries();
    for (int i=0; i<nEvents; i++) {
        tree->GetEntry(i);
        for (int d=0; d<8; d++) {
            if (edep[d] > 1.0) { // 1 MeV threshold (lower than cuboid's 10 MeV
                               // because 10mm disc deposits only ~2-5 MeV per deuteron)
                counts[d]++;
            }
        }
    }
    
    // Ring 0 (20 degrees)
    int N_L_20 = counts[0];
    int N_R_20 = counts[2];
    int N_tot_20 = N_L_20 + N_R_20;
    double eps_20 = 0.0;
    if (N_tot_20 > 0) eps_20 = (double)(N_L_20 - N_R_20) / N_tot_20;
    double fom_20 = N_tot_20 * eps_20 * eps_20;
    
    // Ring 1 (30 degrees)
    int N_L_30 = counts[4];
    int N_R_30 = counts[6];
    int N_tot_30 = N_L_30 + N_R_30;
    double eps_30 = 0.0;
    if (N_tot_30 > 0) eps_30 = (double)(N_L_30 - N_R_30) / N_tot_30;
    double fom_30 = N_tot_30 * eps_30 * eps_30;
    
    cout << "\n=====================================================" << endl;
    cout << "  CYLINDRICAL DIGITAL TWIN (v0700) SHOWDOWN RESULTS  " << endl;
    cout << "  Detector: 40mm diam x 10mm thick disc (N2013 PMT)  " << endl;
    cout << "=====================================================" << endl;
    
    cout << "\nTotal beam events: " << nEvents << endl;
    
    cout << "\n--- All Detector Counts (Edep > 10 MeV) ---" << endl;
    const char* labels[8] = {"R0-Left", "R0-Up", "R0-Right", "R0-Down",
                              "R1-Left", "R1-Up", "R1-Right", "R1-Down"};
    for (int i=0; i<8; i++) {
        cout << "  Det " << i << " (" << labels[i] << "): " << counts[i] << endl;
    }
    
    cout << "\n--- RING 0 (20 Degrees) ---" << endl;
    cout << "  Left Hits (Det 0)  : " << N_L_20 << endl;
    cout << "  Right Hits (Det 2) : " << N_R_20 << endl;
    cout << "  Total LR Hits (N)  : " << N_tot_20 << endl;
    cout << "  Asymmetry (eps)    : " << eps_20 << endl;
    cout << "  Figure of Merit    : " << fom_20 << endl;
    
    cout << "\n--- RING 1 (30 Degrees) ---" << endl;
    cout << "  Left Hits (Det 4)  : " << N_L_30 << endl;
    cout << "  Right Hits (Det 6) : " << N_R_30 << endl;
    cout << "  Total LR Hits (N)  : " << N_tot_30 << endl;
    cout << "  Asymmetry (eps)    : " << eps_30 << endl;
    cout << "  Figure of Merit    : " << fom_30 << endl;
    
    // ===== COMPARISON WITH CUBOID (v0500) =====
    cout << "\n=====================================================" << endl;
    cout << "  HEAD-TO-HEAD: CUBOID (v0500) vs CYLINDER (v0700)   " << endl;
    cout << "=====================================================" << endl;
    
    // v0500 results (from previous run, hardcoded for reference)
    double cuboid_fom_20 = 292.529;
    double cuboid_fom_30 = 394.333;
    double cuboid_eps_20 = -0.515924;
    double cuboid_eps_30 = -0.619048;
    int cuboid_N_20 = 1099;
    int cuboid_N_30 = 1029;
    
    cout << "\n           | Cuboid (v0500) | Cylinder (v0700) " << endl;
    cout << "  ---------+----------------+------------------" << endl;
    cout << Form("  20 deg N | %14d | %16d", cuboid_N_20, N_tot_20) << endl;
    cout << Form("  20 deg e | %14.4f | %16.4f", cuboid_eps_20, eps_20) << endl;
    cout << Form("  20 deg F | %14.1f | %16.1f", cuboid_fom_20, fom_20) << endl;
    cout << "  ---------+----------------+------------------" << endl;
    cout << Form("  30 deg N | %14d | %16d", cuboid_N_30, N_tot_30) << endl;
    cout << Form("  30 deg e | %14.4f | %16.4f", cuboid_eps_30, eps_30) << endl;
    cout << Form("  30 deg F | %14.1f | %16.1f", cuboid_fom_30, fom_30) << endl;

    cout << "\n=====================================================" << endl;
    if (fom_20 > fom_30 && fom_20 > 0) {
        cout << "  CYLINDER WINNER: 20 Degrees" << endl;
    } else if (fom_30 > 0) {
        cout << "  CYLINDER WINNER: 30 Degrees" << endl;
    } else {
        cout << "  WARNING: No hits detected! Need more beam events." << endl;
    }
    
    double best_cyl = max(fom_20, fom_30);
    double best_cub = max(cuboid_fom_20, cuboid_fom_30);
    cout << Form("\n  Best Cuboid FOM:    %.1f", best_cub) << endl;
    cout << Form("  Best Cylinder FOM:  %.1f", best_cyl) << endl;
    cout << Form("  Ratio (Cub/Cyl):    %.1f", best_cub / max(best_cyl, 0.001)) << endl;
    cout << "=============================================\n" << endl;
}
