#include "DET01EventAction.hh"
#include "DET01Hit.hh"
#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4Run.hh"
#include "G4SDManager.hh"
#include "G4AnalysisManager.hh"
#include "G4SystemOfUnits.hh"
#include <iomanip>

// Number of detectors in the geometry (2 rings × 8 per ring)
static const G4int kNDet = 16;

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

  // Per-detector data arrays
  G4double edep[kNDet];
  G4int    pe[kNDet];
  G4double hitTime[kNDet];
  G4ThreeVector posIn[kNDet];
  G4ThreeVector posOut[kNDet];

  for (G4int d = 0; d < kNDet; d++) {
      edep[d]    = 0.;
      pe[d]      = 0;
      hitTime[d] = 99999.*ns;
  }

  // Process Scintillator Hits (Energy + Position)
  if (scintHC) {
      for (size_t i = 0; i < scintHC->entries(); i++) {
          DET01Hit* hit = (*scintHC)[i];
          G4int id = hit->GetDetID();
          
          if (id >= 0 && id < kNDet) {
              edep[id] += hit->GetEdep();
              
              // Track primary particle entry/exit position
              if (hit->GetHasPrimary()) {
                  posIn[id]  = hit->GetPosIn();
                  posOut[id] = hit->GetPosOut();
              }
          }
      }
  }

  // Process PMT Hits (Optical Photons)
  if (pmtHC) {
      for (size_t i = 0; i < pmtHC->entries(); i++) {
          DET01Hit* hit = (*pmtHC)[i];
          G4int id = hit->GetDetID();
          G4double t = hit->GetTime();
          
          if (id >= 0 && id < kNDet) {
              pe[id]++;
              if (t < hitTime[id]) hitTime[id] = t;
          }
      }
  }
  
  // Fix time if no hits
  for (G4int d = 0; d < kNDet; d++) {
      if (pe[d] == 0) hitTime[d] = -1.0;
  }

  // Get Truth Z
  G4double truthZ = event->GetPrimaryVertex(0)->GetPosition().z();

  // Fill Ntuple
  // Col 0: EventID
  analysisManager->FillNtupleIColumn(0, event->GetEventID());
  
  // Cols 1..16: Energy deposition per scintillator
  for (G4int d = 0; d < kNDet; d++) {
      analysisManager->FillNtupleDColumn(1 + d, edep[d]);
  }

  // Cols 17..32: Photoelectron count per PMT
  for (G4int d = 0; d < kNDet; d++) {
      analysisManager->FillNtupleIColumn(1 + kNDet + d, pe[d]);
  }

  // Cols 33..48: First-hit time per PMT
  for (G4int d = 0; d < kNDet; d++) {
      analysisManager->FillNtupleDColumn(1 + 2*kNDet + d, hitTime[d]);
  }

  // Cols 49..144: Position data (6 per detector)
  G4int col = 1 + 3*kNDet;
  for (G4int d = 0; d < kNDet; d++) {
      analysisManager->FillNtupleDColumn(col++, posIn[d].x());
      analysisManager->FillNtupleDColumn(col++, posIn[d].y());
      analysisManager->FillNtupleDColumn(col++, posIn[d].z());
      analysisManager->FillNtupleDColumn(col++, posOut[d].x());
      analysisManager->FillNtupleDColumn(col++, posOut[d].y());
      analysisManager->FillNtupleDColumn(col++, posOut[d].z());
  }
  
  // Col 145: Truth Z
  analysisManager->FillNtupleDColumn(col, truthZ);
  
  analysisManager->AddNtupleRow();

  // Progress Reporting
  G4int eventID = event->GetEventID();
  if ((eventID + 1) % 10000 == 0) {
      const G4Run* currentRun = G4RunManager::GetRunManager()->GetCurrentRun();
      if (currentRun) {
          G4int nTotal = currentRun->GetNumberOfEventToBeProcessed();
          G4cout << "Progress: " << (eventID + 1) << " / " << nTotal 
                 << " (" << std::fixed << std::setprecision(1) 
                 << (100.0 * (eventID + 1) / nTotal) << "%)" << G4endl;
      }
  }
}
