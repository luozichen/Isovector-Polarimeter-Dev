#ifndef DET01SensitiveDetector_h
#define DET01SensitiveDetector_h 1

#include "G4VSensitiveDetector.hh"
#include "DET01Hit.hh"

class G4Step;
class G4HCofThisEvent;

class DET01SensitiveDetector : public G4VSensitiveDetector
{
  public:
    DET01SensitiveDetector(const G4String& name, const G4String& hitsCollectionName);
    virtual ~DET01SensitiveDetector();

    virtual void   Initialize(G4HCofThisEvent* hitCollection);
    virtual G4bool ProcessHits(G4Step* step, G4TouchableHistory* history);
    virtual void   EndOfEvent(G4HCofThisEvent* hitCollection);

  private:
    DET01HitsCollection* fHitsCollection;
};

#endif
