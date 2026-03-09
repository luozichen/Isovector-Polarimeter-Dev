#include "DET01RunAction.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4AnalysisManager.hh"
#include "G4SystemOfUnits.hh"
#include <string>

// Number of detectors in the geometry (2 rings × 8 per ring)
static const G4int kNDet = 16;

DET01RunAction::DET01RunAction()
 : G4UserRunAction()
{
  // Get analysis manager
  auto analysisManager = G4AnalysisManager::Instance();
  analysisManager->SetDefaultFileType("root"); 
  analysisManager->SetVerboseLevel(1);
  analysisManager->SetNtupleMerging(true);

  // Creating Ntuple — columns are created in loops for all 16 detectors
  analysisManager->CreateNtuple("ScatteringData", "Deuteron Scattering Events");
  analysisManager->CreateNtupleIColumn("EventID");      // Col 0

  // Energy deposition per scintillator: Cols 1..16
  for (G4int i = 0; i < kNDet; i++) {
      analysisManager->CreateNtupleDColumn("Edep_Scin" + std::to_string(i));
  }

  // Photoelectron count per PMT: Cols 17..32
  for (G4int i = 0; i < kNDet; i++) {
      analysisManager->CreateNtupleIColumn("PE_PMT" + std::to_string(i));
  }

  // First-hit time per PMT: Cols 33..48
  for (G4int i = 0; i < kNDet; i++) {
      analysisManager->CreateNtupleDColumn("Time_PMT" + std::to_string(i));
  }

  // Primary particle entry/exit position per scintillator: Cols 49..144
  // 6 columns per detector (InX, InY, InZ, OutX, OutY, OutZ)
  for (G4int i = 0; i < kNDet; i++) {
      std::string s = std::to_string(i);
      analysisManager->CreateNtupleDColumn("Scin" + s + "_InX");
      analysisManager->CreateNtupleDColumn("Scin" + s + "_InY");
      analysisManager->CreateNtupleDColumn("Scin" + s + "_InZ");
      analysisManager->CreateNtupleDColumn("Scin" + s + "_OutX");
      analysisManager->CreateNtupleDColumn("Scin" + s + "_OutY");
      analysisManager->CreateNtupleDColumn("Scin" + s + "_OutZ");
  }

  analysisManager->CreateNtupleDColumn("Truth_Z");      // Col 145
  analysisManager->FinishNtuple();
}

DET01RunAction::~DET01RunAction()
{
}

void DET01RunAction::BeginOfRunAction(const G4Run*)
{
  // Get analysis manager
  auto analysisManager = G4AnalysisManager::Instance();

  // Open an output file
  G4String fileName = analysisManager->GetFileName();
  if (fileName.empty()) {
    fileName = "DET01_Scattering_Result";
  }
  analysisManager->OpenFile(fileName);
}

void DET01RunAction::EndOfRunAction(const G4Run*)
{
  // Get analysis manager
  auto analysisManager = G4AnalysisManager::Instance();

  // Write and close
  analysisManager->Write();
  analysisManager->CloseFile();
}
