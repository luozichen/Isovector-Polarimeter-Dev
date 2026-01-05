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
  analysisManager->SetDefaultFileType("csv"); 
  analysisManager->SetVerboseLevel(1);
  analysisManager->SetNtupleMerging(true);

  // Creating histograms
  // ID 0: Energy Deposition in Detector 0
  analysisManager->CreateH1("Edep_Det0", "Energy Deposition in Detector 0", 100, 0., 80.*MeV);
  
  // ID 1: Energy Deposition in Detector 1
  analysisManager->CreateH1("Edep_Det1", "Energy Deposition in Detector 1", 100, 0., 80.*MeV);
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
