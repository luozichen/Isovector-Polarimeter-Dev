#ifndef PolarimeterSD_h
#define PolarimeterSD_h 1

#include "G4VSensitiveDetector.hh"
#include "globals.hh"

class G4Step;
class G4HCofThisEvent;
class G4TouchableHistory;
class TSimData;

// Sensitive detector for polarimeter scintillator bars.
// Records hit data using the smsimulator TSimData format
// and stores into SimDataManager's TClonesArray.

class PolarimeterSD : public G4VSensitiveDetector
{
  public:
    PolarimeterSD(const G4String& name);
    virtual ~PolarimeterSD();

    virtual void   Initialize(G4HCofThisEvent*);
    virtual G4bool ProcessHits(G4Step* step, G4TouchableHistory*);
    virtual void   EndOfEvent(G4HCofThisEvent*);

  private:
    G4String fDetectorName;
};

#endif
