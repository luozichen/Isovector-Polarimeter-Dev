#include "DET01RunAction.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4AnalysisManager.hh"
#include "G4SystemOfUnits.hh"

DET01RunAction::DET01RunAction()
 : G4UserRunAction()
{
  // Get analysis manager
  auto analysisManager = G4AnalysisManager::Instance();
  analysisManager->SetDefaultFileType("root"); 
  analysisManager->SetVerboseLevel(1);
  analysisManager->SetNtupleMerging(true);

  // Creating Ntuple
  analysisManager->CreateNtuple("CosmicData", "Cosmic Ray Events");
  analysisManager->CreateNtupleIColumn("EventID");      // ID 0
  analysisManager->CreateNtupleDColumn("Edep_Scin0");   // ID 1
  analysisManager->CreateNtupleDColumn("Edep_Scin1");   // ID 2
  analysisManager->CreateNtupleDColumn("Edep_Scin2");   // ID 3
  analysisManager->CreateNtupleDColumn("Edep_Scin3");   // ID 4
  analysisManager->CreateNtupleIColumn("PE_PMT0");      // ID 5
  analysisManager->CreateNtupleIColumn("PE_PMT1");      // ID 6
  analysisManager->CreateNtupleIColumn("PE_PMT2");      // ID 7
  analysisManager->CreateNtupleIColumn("PE_PMT3");      // ID 8
  analysisManager->CreateNtupleDColumn("Time_PMT0");    // ID 9
  analysisManager->CreateNtupleDColumn("Time_PMT1");    // ID 10
  analysisManager->CreateNtupleDColumn("Time_PMT2");    // ID 11
  analysisManager->CreateNtupleDColumn("Time_PMT3");    // ID 12

  // Position Data (Primary Muon)
  // Scin0
  analysisManager->CreateNtupleDColumn("Scin0_InX");    // ID 13
  analysisManager->CreateNtupleDColumn("Scin0_InY");    // ID 14
  analysisManager->CreateNtupleDColumn("Scin0_InZ");    // ID 15
  analysisManager->CreateNtupleDColumn("Scin0_OutX");   // ID 16
  analysisManager->CreateNtupleDColumn("Scin0_OutY");   // ID 17
  analysisManager->CreateNtupleDColumn("Scin0_OutZ");   // ID 18
  // Scin1
  analysisManager->CreateNtupleDColumn("Scin1_InX");    // ID 19
  analysisManager->CreateNtupleDColumn("Scin1_InY");    // ID 20
  analysisManager->CreateNtupleDColumn("Scin1_InZ");    // ID 21
  analysisManager->CreateNtupleDColumn("Scin1_OutX");   // ID 22
  analysisManager->CreateNtupleDColumn("Scin1_OutY");   // ID 23
  analysisManager->CreateNtupleDColumn("Scin1_OutZ");   // ID 24
  // Scin2
  analysisManager->CreateNtupleDColumn("Scin2_InX");    // ID 25
  analysisManager->CreateNtupleDColumn("Scin2_InY");    // ID 26
  analysisManager->CreateNtupleDColumn("Scin2_InZ");    // ID 27
  analysisManager->CreateNtupleDColumn("Scin2_OutX");   // ID 28
  analysisManager->CreateNtupleDColumn("Scin2_OutY");   // ID 29
  analysisManager->CreateNtupleDColumn("Scin2_OutZ");   // ID 30
  // Scin3
  analysisManager->CreateNtupleDColumn("Scin3_InX");    // ID 31
  analysisManager->CreateNtupleDColumn("Scin3_InY");    // ID 32
  analysisManager->CreateNtupleDColumn("Scin3_InZ");    // ID 33
  analysisManager->CreateNtupleDColumn("Scin3_OutX");   // ID 34
  analysisManager->CreateNtupleDColumn("Scin3_OutY");   // ID 35
  analysisManager->CreateNtupleDColumn("Scin3_OutZ");   // ID 36

  analysisManager->CreateNtupleDColumn("Truth_Z");      // ID 37
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
  G4String fileName = "DET01_Cosmic_Result";
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
