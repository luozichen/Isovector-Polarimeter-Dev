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
  analysisManager->CreateNtupleIColumn("PE_PMT0");      // ID 3
  analysisManager->CreateNtupleIColumn("PE_PMT1");      // ID 4
  analysisManager->CreateNtupleDColumn("Time_PMT0");    // ID 5
  analysisManager->CreateNtupleDColumn("Time_PMT1");    // ID 6
  analysisManager->CreateNtupleDColumn("Truth_Z");      // ID 7
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
