// ============================================================
// analysis_example.cc
// Example ROOT macro for analysing sim_polarimeter output
//
// Usage:
//   root -l rootlogon.C
//   root [0] .x macros/examples/analysis_example.cc("polarimeter_pencil0001.root")
// ============================================================

#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TCanvas.h"
#include "TClonesArray.h"
#include "TSimData.hh"
#include "TBeamSimData.hh"
#include <iostream>
#include <cmath>

void analysis_example(const char* filename = "polarimeter_pencil0001.root")
{
  // Open file
  TFile* f = new TFile(filename, "READ");
  if (!f || f->IsZombie()) {
    std::cerr << "Error: Cannot open " << filename << std::endl;
    return;
  }

  TTree* tree = (TTree*)f->Get("tree");
  if (!tree) {
    std::cerr << "Error: Cannot find 'tree' in file." << std::endl;
    return;
  }

  Long64_t nEntries = tree->GetEntries();
  std::cout << "Number of events: " << nEntries << std::endl;

  // Set branch addresses
  TClonesArray* polSimDataArray = new TClonesArray("TSimData", 100);
  tree->SetBranchAddress("PolarimeterSimData", &polSimDataArray);

  // Histograms
  const int nDet = 16;
  TH1D* hEdep[nDet];
  for (int i = 0; i < nDet; i++) {
    hEdep[i] = new TH1D(Form("hEdep_%d", i),
                         Form("Energy Deposit in Scintillator %d;E_{dep} [MeV];Counts", i),
                         200, 0, 100);
  }

  TH1D* hDetHit = new TH1D("hDetHit", "Detector Hit Multiplicity;Detector ID;Counts",
                             nDet, -0.5, nDet - 0.5);

  TH2D* hXY = new TH2D("hXY", "Hit Position (X vs Y);X [mm];Y [mm]",
                         200, -2000, 2000, 200, -2000, 2000);

  // Event loop
  for (Long64_t ev = 0; ev < nEntries; ev++) {
    tree->GetEntry(ev);

    // Sum energy per detector for this event
    double edepSum[nDet] = {0};

    Int_t nHits = polSimDataArray->GetEntries();
    for (Int_t i = 0; i < nHits; i++) {
      TSimData* sd = (TSimData*)polSimDataArray->At(i);
      if (!sd) continue;

      int detID = sd->fDetID;
      if (detID >= 0 && detID < nDet) {
        edepSum[detID] += sd->fEnergyDeposit;

        // Hit position
        hXY->Fill(sd->fPrePosition.X(), sd->fPrePosition.Y());
      }
    }

    // Fill histograms
    for (int d = 0; d < nDet; d++) {
      if (edepSum[d] > 0) {
        hEdep[d]->Fill(edepSum[d]);
        hDetHit->Fill(d);
      }
    }
  }

  // Draw results
  TCanvas* c1 = new TCanvas("c1", "Polarimeter Analysis", 1200, 800);
  c1->Divide(4, 4);
  for (int i = 0; i < nDet; i++) {
    c1->cd(i + 1);
    hEdep[i]->Draw();
  }

  TCanvas* c2 = new TCanvas("c2", "Hit Summary", 800, 400);
  c2->Divide(2, 1);
  c2->cd(1);
  hDetHit->Draw();
  c2->cd(2);
  hXY->Draw("COLZ");

  // Print summary
  std::cout << "\n=== Detector Hit Summary ===" << std::endl;
  for (int d = 0; d < nDet; d++) {
    int ring = d / 8;
    int idx  = d % 8;
    double phi = idx * 45.0;
    std::cout << Form("  Det %2d (Ring %d, phi=%5.1f deg): %d hits, <Edep>=%.2f MeV",
                       d, ring, phi,
                       (int)hDetHit->GetBinContent(d + 1),
                       hEdep[d]->GetMean())
              << std::endl;
  }
}
