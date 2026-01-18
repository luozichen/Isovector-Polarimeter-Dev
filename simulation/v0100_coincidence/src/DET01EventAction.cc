#include "DET01EventAction.hh"
#include "DET01Hit.hh"
#include "G4Event.hh"
#include "G4SDManager.hh"
#include "G4AnalysisManager.hh"
#include "G4SystemOfUnits.hh"

DET01EventAction::DET01EventAction()
: G4UserEventAction(),
  fScintHCID(-1),
  fPmtHCID(-1)
{} 

DET01EventAction::~DET01EventAction()
{}

void DET01EventAction::BeginOfEventAction(const G4Event*)
{}

void DET01EventAction::EndOfEventAction(const G4Event* event)
{
  // Get Analysis Manager
  auto analysisManager = G4AnalysisManager::Instance();

  // Get Hits Collections IDs (only once)
  if (fScintHCID == -1) {
      fScintHCID = G4SDManager::GetSDMpointer()->GetCollectionID("ScintSD/ScintHitsCollection");
      fPmtHCID   = G4SDManager::GetSDMpointer()->GetCollectionID("PmtSD/HitsCollection");
  }

  // Get Hits Collections
  G4HCofThisEvent* hce = event->GetHCofThisEvent();
  if (!hce) return;

  DET01HitsCollection* scintHC = nullptr;
  if (fScintHCID != -1) {
      scintHC = static_cast<DET01HitsCollection*>(hce->GetHC(fScintHCID));
  }
    
  DET01HitsCollection* pmtHC = nullptr;
  if (fPmtHCID != -1) {
      pmtHC = static_cast<DET01HitsCollection*>(hce->GetHC(fPmtHCID));
  }

  // Variables to store data
  G4double edep0 = 0.;
  G4double edep1 = 0.;
  
  G4int pe0 = 0;
  G4int pe1 = 0;
  
  G4double time0 = 99999.*ns; // Init with large value
  G4double time1 = 99999.*ns;

  // Process Scintillator Hits (Energy)
  if (scintHC) {
      for (size_t i=0; i<scintHC->entries(); i++) {
          DET01Hit* hit = (*scintHC)[i];
          if (hit->GetDetID() == 0) edep0 += hit->GetEdep();
          if (hit->GetDetID() == 1) edep1 += hit->GetEdep();
      }
  }

  // Process PMT Hits (Photons)
  if (pmtHC) {
      for (size_t i=0; i<pmtHC->entries(); i++) {
          DET01Hit* hit = (*pmtHC)[i];
          G4int id = hit->GetDetID();
          G4double t = hit->GetTime();
          
          if (id == 0) {
              pe0++;
              if (t < time0) time0 = t;
          }
          if (id == 1) {
              pe1++;
              if (t < time1) time1 = t;
          }
      }
  }
  
  // Fix time if no hits
  if (pe0 == 0) time0 = -1.0;
  if (pe1 == 0) time1 = -1.0;

  // Get Truth Z (Primary Vertex Position)
  // Assumes at least one vertex exists (always true for GPS)
  G4double truthZ = event->GetPrimaryVertex(0)->GetPosition().z();

  // Fill Ntuple
  // Column order must match RunAction
  analysisManager->FillNtupleIColumn(0, event->GetEventID());
  analysisManager->FillNtupleDColumn(1, edep0);
  analysisManager->FillNtupleDColumn(2, edep1);
  analysisManager->FillNtupleIColumn(3, pe0);
  analysisManager->FillNtupleIColumn(4, pe1);
  analysisManager->FillNtupleDColumn(5, time0);
  analysisManager->FillNtupleDColumn(6, time1);
  analysisManager->FillNtupleDColumn(7, truthZ);
  
  analysisManager->AddNtupleRow();
}
