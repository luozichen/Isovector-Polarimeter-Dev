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
  G4double edep0 = 0., edep1 = 0., edep2 = 0., edep3 = 0.;
  G4int pe0 = 0, pe1 = 0, pe2 = 0, pe3 = 0;
  G4double time0 = 99999.*ns, time1 = 99999.*ns, time2 = 99999.*ns, time3 = 99999.*ns;
  
  // Position Data (Default 0,0,0)
  G4ThreeVector posIn[4];
  G4ThreeVector posOut[4];

  // Process Scintillator Hits (Energy + Position)
  if (scintHC) {
      for (size_t i=0; i<scintHC->entries(); i++) {
          DET01Hit* hit = (*scintHC)[i];
          G4int id = hit->GetDetID();
          
          if (id >= 0 && id < 4) {
              if (id == 0) edep0 += hit->GetEdep();
              if (id == 1) edep1 += hit->GetEdep();
              if (id == 2) edep2 += hit->GetEdep();
              if (id == 3) edep3 += hit->GetEdep();
              
              if (hit->GetHasPrimary()) {
                  posIn[id] = hit->GetPosIn();
                  posOut[id] = hit->GetPosOut();
              }
          }
      }
  }

  // Process PMT Hits (Photons)
  if (pmtHC) {
      for (size_t i=0; i<pmtHC->entries(); i++) {
          DET01Hit* hit = (*pmtHC)[i];
          G4int id = hit->GetDetID();
          G4double t = hit->GetTime();
          
          if (id == 0) { pe0++; if (t < time0) time0 = t; }
          if (id == 1) { pe1++; if (t < time1) time1 = t; }
          if (id == 2) { pe2++; if (t < time2) time2 = t; }
          if (id == 3) { pe3++; if (t < time3) time3 = t; }
      }
  }
  
  // Fix time if no hits
  if (pe0 == 0) time0 = -1.0;
  if (pe1 == 0) time1 = -1.0;
  if (pe2 == 0) time2 = -1.0;
  if (pe3 == 0) time3 = -1.0;

  // Get Truth Z
  G4double truthZ = event->GetPrimaryVertex(0)->GetPosition().z();

  // Fill Ntuple
  analysisManager->FillNtupleIColumn(0, event->GetEventID());
  
  analysisManager->FillNtupleDColumn(1, edep0);
  analysisManager->FillNtupleDColumn(2, edep1);
  analysisManager->FillNtupleDColumn(3, edep2);
  analysisManager->FillNtupleDColumn(4, edep3);
  
  analysisManager->FillNtupleIColumn(5, pe0);
  analysisManager->FillNtupleIColumn(6, pe1);
  analysisManager->FillNtupleIColumn(7, pe2);
  analysisManager->FillNtupleIColumn(8, pe3);
  
  analysisManager->FillNtupleDColumn(9, time0);
  analysisManager->FillNtupleDColumn(10, time1);
  analysisManager->FillNtupleDColumn(11, time2);
  analysisManager->FillNtupleDColumn(12, time3);
  
  // Fill Positions (13-36)
  int col = 13;
  for(int i=0; i<4; i++) {
      analysisManager->FillNtupleDColumn(col++, posIn[i].x());
      analysisManager->FillNtupleDColumn(col++, posIn[i].y());
      analysisManager->FillNtupleDColumn(col++, posIn[i].z());
      analysisManager->FillNtupleDColumn(col++, posOut[i].x());
      analysisManager->FillNtupleDColumn(col++, posOut[i].y());
      analysisManager->FillNtupleDColumn(col++, posOut[i].z());
  }
  
  analysisManager->FillNtupleDColumn(37, truthZ);
  
  analysisManager->AddNtupleRow();
}
