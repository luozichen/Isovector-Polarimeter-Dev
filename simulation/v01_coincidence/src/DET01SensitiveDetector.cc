#include "DET01SensitiveDetector.hh"
#include "DET01Hit.hh"
#include "G4HCofThisEvent.hh"
#include "G4Step.hh"
#include "G4ThreeVector.hh"
#include "G4SDManager.hh"
#include "G4ios.hh"
#include "G4OpticalPhoton.hh"

DET01SensitiveDetector::DET01SensitiveDetector(const G4String& name,
                                               const G4String& hitsCollectionName)
 : G4VSensitiveDetector(name),
   fHitsCollection(nullptr)
{
  collectionName.insert(hitsCollectionName);
}

DET01SensitiveDetector::~DET01SensitiveDetector()
{}

void DET01SensitiveDetector::Initialize(G4HCofThisEvent* hce)
{
  // Create hits collection
  fHitsCollection = new DET01HitsCollection(SensitiveDetectorName, collectionName[0]);

  // Add this collection in hce
  G4int hcID = GetCollectionID(0);
  hce->AddHitsCollection(hcID, fHitsCollection);
}

G4bool DET01SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*)
{
  // Only detect optical photons
  G4ParticleDefinition* particleType = step->GetTrack()->GetDefinition();
  if(particleType != G4OpticalPhoton::OpticalPhotonDefinition()) return false;

  // Create new hit
  DET01Hit* newHit = new DET01Hit();
  newHit->SetTime(step->GetPostStepPoint()->GetGlobalTime());
  
  // Identify which detector was hit
  // The Photocathode is placed into World with a specific Copy Number in Construct()
  // 0 = Bottom (or Top depending on loop), 1 = The other one.
  G4int detID = step->GetPreStepPoint()->GetTouchable()->GetReplicaNumber(0);
  newHit->SetDetID(detID);

  // Insert hit into collection
  fHitsCollection->insert(newHit);
  
  // Kill the photon
  step->GetTrack()->SetTrackStatus(fStopAndKill);

  return true;
}

void DET01SensitiveDetector::EndOfEvent(G4HCofThisEvent*)
{
  G4int nofHits = fHitsCollection->entries();
  if (nofHits > 0) {
      G4int count0 = 0;
      G4int count1 = 0;
      
      for(size_t i=0; i<fHitsCollection->GetSize(); i++) {
          DET01Hit* hit = static_cast<DET01Hit*>(fHitsCollection->GetHit(i));
          if(hit->GetDetID() == 0) count0++;
          else if(hit->GetDetID() == 1) count1++;
      }
      
      G4cout << "Use log: Event Summary -> DET_0: " << count0 << " photons, DET_1: " << count1 << " photons." << G4endl;
  }
}
