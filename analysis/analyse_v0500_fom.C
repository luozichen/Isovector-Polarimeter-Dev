void analyse_v0500_fom() {
    TFile *f = TFile::Open("simulation/v0500_cuboid_twin/build/DET01_Scattering_Result.root");
    if (!f || f->IsZombie()) {
        cout << "Error opening file!" << endl;
        return;
    }

    TTree *tree = (TTree*)f->Get("ScatteringData");
    if (!tree) {
        cout << "Error finding tree!" << endl;
        return;
    }

    // We will count the number of hits for each detector that pass the 10 MeV threshold
    // 20 degree ring: 0 (Left), 1 (Up), 2 (Right), 3 (Down)
    // 30 degree ring: 4 (Left), 5 (Up), 6 (Right), 7 (Down)
    
    int counts[8] = {0};
    double edep[8];
    for (int i=0; i<8; i++) {
        tree->SetBranchAddress(Form("Edep_Scin%d", i), &edep[i]);
    }
    
    int nEvents = tree->GetEntries();
    for (int i=0; i<nEvents; i++) {
        tree->GetEntry(i);
        for (int d=0; d<8; d++) {
            if (edep[d] > 10.0) { // 10 MeV energy threshold to reject crosstalk
                counts[d]++;
            }
        }
    }
    
    // Ring 0 (20 degrees)
    int N_L_30 = counts[0];
    int N_R_30 = counts[2];
    int N_tot_30 = N_L_30 + N_R_30;
    double eps_30 = 0.0;
    if (N_tot_30 > 0) eps_30 = (double)(N_L_30 - N_R_30) / N_tot_30;
    double fom_30 = N_tot_30 * eps_30 * eps_30;
    
    // Ring 1 (30 degrees)
    int N_L_45 = counts[4];
    int N_R_45 = counts[6];
    int N_tot_45 = N_L_45 + N_R_45;
    double eps_45 = 0.0;
    if (N_tot_45 > 0) eps_45 = (double)(N_L_45 - N_R_45) / N_tot_45;
    double fom_45 = N_tot_45 * eps_45 * eps_45;
    
    cout << "\n=============================================" << endl;
    cout << "  CUBOID DIGITAL TWIN (v0500) SHOWDOWN RESULTS " << endl;
    cout << "=============================================\n" << endl;
    
    cout << "RING 0 (20 Degrees):" << endl;
    cout << "  Left Hits (Det 0)  : " << N_L_30 << endl;
    cout << "  Right Hits (Det 2) : " << N_R_30 << endl;
    cout << "  Total LR Hits (N)  : " << N_tot_30 << endl;
    cout << "  Asymmetry (eps)    : " << eps_30 << endl;
    cout << "  Figure of Merit    : " << fom_30 << "\n" << endl;
    
    cout << "RING 1 (30 Degrees):" << endl;
    cout << "  Left Hits (Det 4)  : " << N_L_45 << endl;
    cout << "  Right Hits (Det 6) : " << N_R_45 << endl;
    cout << "  Total LR Hits (N)  : " << N_tot_45 << endl;
    cout << "  Asymmetry (eps)    : " << eps_45 << endl;
    cout << "  Figure of Merit    : " << fom_45 << "\n" << endl;
    
    cout << "=============================================" << endl;
    if (fom_30 > fom_45) {
        cout << "  WINNER: 20 Degrees (Higher Statistical Power)" << endl;
    } else {
        cout << "  WINNER: 30 Degrees (Higher Statistical Power)" << endl;
    }
    cout << "=============================================\n" << endl;
}
