#ifndef DET01ScintSD_h
#define DET01ScintSD_h 1

#include "G4VSensitiveDetector.hh"
#include "DET01Hit.hh"

class DET01ScintSD : public G4VSensitiveDetector
{
  public:
    DET01ScintSD(const G4String& name, const G4String& hitsCollectionName);
    virtual ~DET01ScintSD();

    // Methods from base class
    virtual void   Initialize(G4HCofThisEvent* hitCollection);
    virtual G4bool ProcessHits(G4Step* step, G4TouchableHistory* history);
    virtual void   EndOfEvent(G4HCofThisEvent* hitCollection);

  private:
    DET01HitsCollection* fHitsCollection;
};

#endif
