#ifndef PolarimeterDetectorConstructionMessenger_h
#define PolarimeterDetectorConstructionMessenger_h 1

#include "G4UImessenger.hh"
#include "globals.hh"

class PolarimeterDetectorConstruction;
class G4UIdirectory;
class G4UIcmdWithADoubleAndUnit;
class G4UIcmdWithAnInteger;
class G4UIcmdWithABool;

class PolarimeterDetectorConstructionMessenger : public G4UImessenger
{
  public:
    PolarimeterDetectorConstructionMessenger(PolarimeterDetectorConstruction*);
    virtual ~PolarimeterDetectorConstructionMessenger();

    virtual void SetNewValue(G4UIcommand*, G4String);

  private:
    PolarimeterDetectorConstruction* fDetector;
    G4UIdirectory*                   fDir;
    G4UIcmdWithADoubleAndUnit*       fDistanceCmd;
    G4UIcmdWithADoubleAndUnit*       fAngle0Cmd;
    G4UIcmdWithADoubleAndUnit*       fAngle1Cmd;
    G4UIcmdWithAnInteger*            fNDetCmd;
    G4UIcmdWithABool*                fUseDipoleCmd;
    G4UIcmdWithABool*                fUseNEBULACmd;
};

#endif
