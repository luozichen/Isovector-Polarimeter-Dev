void extract_v0200_jitter() {
    TFile *f = TFile::Open("simulation/v0200_coincidence/build/DET01_Cosmic_Result_long.root");
    if (!f || f->IsZombie()) {
        cout << "Error opening file" << endl;
        return;
    }

    TTree *tree = (TTree*)f->Get("CoincidenceData");
    if (!tree) {
        cout << "Error finding tree CoincidenceData" << endl;
        return;
    }

    // Create a temporary canvas so the histogram doesn't pop up
    TCanvas *c1 = new TCanvas("c1", "c1", 800, 600);
    
    // We want the standard deviation of the hit times for events that actually had a hit
    // A cut of Edep_Scin0 > 5.0 ensures we only look at real cosmic ray hits
    tree->Draw("Time_PMT0>>hTime0(100, 0, 10)", "Edep_Scin0 > 5.0", "goff");
    
    TH1F *hTime0 = (TH1F*)gDirectory->Get("hTime0");
    if (hTime0) {
        double std_dev = hTime0->GetStdDev();
        cout << "\n=============================================" << endl;
        cout << "Optical Jitter (Std Dev) for Det 0: " << std_dev << " ns" << endl;
        cout << "=============================================\n" << endl;
    } else {
        cout << "Could not create histogram." << endl;
    }
}
