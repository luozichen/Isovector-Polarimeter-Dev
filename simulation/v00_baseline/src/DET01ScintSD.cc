#include "DET01ScintSD.hh"
#include "G4HCofThisEvent.hh"
#include "G4Step.hh"
#include "G4ThreeVector.hh"
#include "G4SDManager.hh"
#include "G4UnitsTable.hh"
#include "G4AnalysisManager.hh"
#include "G4ios.hh"

DET01ScintSD::DET01ScintSD(const G4String& name,
                         const G4String& hitsCollectionName)
 : G4VSensitiveDetector(name),
   fHitsCollection(nullptr)
{
  collectionName.insert(hitsCollectionName);
}

DET01ScintSD::~DET01ScintSD()
{}

void DET01ScintSD::Initialize(G4HCofThisEvent* hce)
{
  // Create hits collection
  fHitsCollection = new DET01HitsCollection(SensitiveDetectorName, collectionName[0]);

  // Add this collection in hce
  G4int hcID = G4SDManager::GetSDMpointer()->GetCollectionID(collectionName[0]);
  hce->AddHitsCollection(hcID, fHitsCollection);
}

G4bool DET01ScintSD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
  // Get energy deposit
  G4double edep = step->GetTotalEnergyDeposit();

  if (edep == 0.) return false;

  // We are inside the Scintillator.
  // Identify which detector (Top=0 or Bottom=1)
  // Since we used PVPlacement with copy numbers in the loop in DetectorConstruction:
  G4int detID = step->GetPreStepPoint()->GetTouchable()->GetCopyNumber();

  // Check if we already have a hit for this detector in this event
  // If so, add energy to it. If not, create new.
  
  DET01Hit* hit = nullptr;
  
  // Simple linear search (since only 2 detectors, it's fast)
  for(size_t i=0; i<fHitsCollection->entries(); i++) {
      DET01Hit* existingHit = (*fHitsCollection)[i];
      if(existingHit->GetDetID() == detID) {
          hit = existingHit;
          break;
      }
  }

  if(!hit) {
      hit = new DET01Hit();
      hit->SetDetID(detID);
      fHitsCollection->insert(hit);
  }

  // Add Energy
  hit->AddEdep(edep);

  return true;
}

void DET01ScintSD::EndOfEvent(G4HCofThisEvent*)
{
    // Fill Histograms
    auto analysisManager = G4AnalysisManager::Instance();

    G4int nofHits = fHitsCollection->entries();
    for (G4int i = 0; i < nofHits; i++) {
        DET01Hit* hit = (*fHitsCollection)[i];
        G4int id = hit->GetDetID();
        G4double edep = hit->GetEdep();

        // Check ID range to be safe (we have 0 and 1)
        if(id >= 0 && id <= 1) {
             analysisManager->FillH1(id, edep);
        }
    }
}
