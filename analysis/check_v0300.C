void check_v0300() {
    TFile *f = TFile::Open("simulation/v0300_scattering/build/DET01_Scattering_Result.root");
    if (!f || f->IsZombie()) {
        cout << "Error opening file" << endl;
        return;
    }

    TTree *tree = (TTree*)f->Get("ScatteringData");
    if (!tree) {
        cout << "Error: ScatteringData tree not found" << endl;
        return;
    }

    // Indices for 30 degree ring: L=8, U=10, R=12, D=14
    // We apply a realistic "Discriminator Threshold" of 10 MeV deposited energy.
    // This prevents counting single-photon crosstalk or secondary gammas as a "Deuteron hit"
    long L_hits = tree->GetEntries("Edep_Scin8 > 10.0");
    long U_hits = tree->GetEntries("Edep_Scin10 > 10.0");
    long R_hits = tree->GetEntries("Edep_Scin12 > 10.0");
    long D_hits = tree->GetEntries("Edep_Scin14 > 10.0");

    cout << "\n--- Results for 30-degree Ring (1000 events) ---" << endl;
    cout << "N_L (0 deg)  : " << L_hits << endl;
    cout << "N_U (90 deg) : " << U_hits << endl;
    cout << "N_R (180 deg): " << R_hits << endl;
    cout << "N_D (270 deg): " << D_hits << endl;

    if ((L_hits + R_hits) > 0) {
        double epsilon_LR = (L_hits - R_hits) / (double)(L_hits + R_hits);
        cout << "\nLeft-Right Asymmetry (e_LR): " << epsilon_LR << endl;
    }

    if ((L_hits + R_hits + U_hits + D_hits) > 0) {
        double epsilon_T = ((L_hits + R_hits) - (U_hits + D_hits)) / (double)(L_hits + R_hits + U_hits + D_hits);
        cout << "Tensor Asymmetry (e_T)     : " << epsilon_T << endl;
    }
}
