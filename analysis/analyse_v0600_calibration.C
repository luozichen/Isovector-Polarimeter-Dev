// analyse_v0600_calibration.C
// Extracts Landau MPV and optical jitter from the v0600 cylindrical coincidence simulation.
// Usage: root -l -q analysis/analyse_v0600_calibration.C
//   (Run from the repository root directory)

void analyse_v0600_calibration() {
    TFile *f = TFile::Open("simulation/v0600_cylindrical_coincidence/build/DET01_Cosmic_Result_long.root");
    if (!f || f->IsZombie()) {
        cout << "Error opening file!" << endl;
        return;
    }

    TTree *tree = (TTree*)f->Get("CosmicData");
    if (!tree) {
        cout << "Error finding tree!" << endl;
        return;
    }

    cout << "\n=============================================" << endl;
    cout << "  CYLINDRICAL COINCIDENCE (v0600) ANALYSIS   " << endl;
    cout << "  Geometry: 40mm diam x 10mm thick, 5mm gap  " << endl;
    cout << "=============================================\n" << endl;

    cout << "Total events: " << tree->GetEntries() << endl;

    // Coincidence cut: both detectors must have significant PE count
    TCut coincCut = "PE_PMT0>50 && PE_PMT1>50";
    int nCoinc = tree->GetEntries(coincCut);
    cout << "Coincidence events: " << nCoinc << endl;
    cout << "Coincidence rate: " << 100.0 * nCoinc / tree->GetEntries() << " %" << endl;

    // ===== PART 1: LANDAU ENERGY CALIBRATION =====
    TCanvas *c1 = new TCanvas("c1", "Cylindrical Energy Calibration", 1200, 500);
    c1->Divide(2, 1);

    // Det 0 (Top)
    c1->cd(1);
    tree->Draw("Edep_Scin0 >> hEdep0(100, 0, 5)", coincCut);
    TH1F *hEdep0 = (TH1F*)gDirectory->Get("hEdep0");
    hEdep0->SetTitle("Det 0 (Top) Energy Deposition;Energy [MeV];Counts");
    hEdep0->SetLineColor(kBlue);
    hEdep0->SetLineWidth(2);

    // Find the peak region for Landau fit
    int binMax0 = hEdep0->GetMaximumBin();
    double peakPos0 = hEdep0->GetBinCenter(binMax0);
    TF1 *landau0 = new TF1("landau0", "landau", peakPos0 * 0.5, peakPos0 * 2.0);
    hEdep0->Fit(landau0, "RQ");
    double mpv0 = landau0->GetParameter(1);

    // Det 1 (Bottom)
    c1->cd(2);
    tree->Draw("Edep_Scin1 >> hEdep1(100, 0, 5)", coincCut);
    TH1F *hEdep1 = (TH1F*)gDirectory->Get("hEdep1");
    hEdep1->SetTitle("Det 1 (Bottom) Energy Deposition;Energy [MeV];Counts");
    hEdep1->SetLineColor(kRed);
    hEdep1->SetLineWidth(2);

    int binMax1 = hEdep1->GetMaximumBin();
    double peakPos1 = hEdep1->GetBinCenter(binMax1);
    TF1 *landau1 = new TF1("landau1", "landau", peakPos1 * 0.5, peakPos1 * 2.0);
    hEdep1->Fit(landau1, "RQ");
    double mpv1 = landau1->GetParameter(1);

    c1->SaveAs("results/simulation/v0600_landau_fits.png");

    // Average MPV (reference energy for calibration)
    double mpvAvg = (mpv0 + mpv1) / 2.0;

    cout << "\n--- Energy Calibration ---" << endl;
    cout << "  Det 0 Landau MPV: " << mpv0 << " MeV" << endl;
    cout << "  Det 1 Landau MPV: " << mpv1 << " MeV" << endl;
    cout << "  Average MPV:      " << mpvAvg << " MeV" << endl;
    cout << "  (This is the reference energy for MeV/mV conversion)" << endl;

    // ===== PART 2: OPTICAL JITTER =====
    TCanvas *c2 = new TCanvas("c2", "Cylindrical Optical Jitter", 600, 500);
    tree->Draw("Time_PMT0 - Time_PMT1 >> hTime(200, -0.1, 0.1)", coincCut);
    TH1F *hTime = (TH1F*)gDirectory->Get("hTime");
    hTime->SetTitle("Timing Difference (Det 0 - Det 1);#Deltat [ns];Counts");
    hTime->SetLineColor(kBlue);
    hTime->SetLineWidth(2);
    hTime->Fit("gaus", "Q");
    TF1 *gfit = hTime->GetFunction("gaus");
    double sigma_pair = gfit->GetParameter(2);
    double sigma_single = sigma_pair / sqrt(2.0);

    c2->SaveAs("results/simulation/v0600_optical_jitter.png");

    cout << "\n--- Optical Jitter ---" << endl;
    cout << "  Pair sigma:              " << sigma_pair << " ns" << endl;
    cout << "  Single detector sigma:   " << sigma_single << " ns" << endl;

    // ===== SUMMARY =====
    cout << "\n=============================================" << endl;
    cout << "  SUMMARY: CYLINDRICAL vs CUBOID" << endl;
    cout << "=============================================\n" << endl;
    cout << "  Cuboid  sigma_opt: 0.195 ns   (150x150x120 mm)" << endl;
    cout << "  Cylinder sigma_opt: " << sigma_single << " ns   (40x10 mm disc)" << endl;
    cout << "  Reference Energy (Cylinder): " << mpvAvg << " MeV" << endl;
    cout << "  Reference Energy (Cuboid):   30.01 MeV" << endl;
    cout << "\n=============================================\n" << endl;
}
