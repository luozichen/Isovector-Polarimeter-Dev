#ifndef PolarimeterDetectorConstruction_h
#define PolarimeterDetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class G4VPhysicalVolume;
class G4LogicalVolume;
class PolarimeterDetectorConstructionMessenger;

class PolarimeterDetectorConstruction : public G4VUserDetectorConstruction
{
  public:
    PolarimeterDetectorConstruction();
    virtual ~PolarimeterDetectorConstruction();

    virtual G4VPhysicalVolume* Construct();
    virtual void ConstructSDandField();

    // Setters for messenger
    void SetTargetDistance(G4double d) { fTargetDistance = d; }
    void SetAngleRing0(G4double a)    { fAngleRing0 = a; }
    void SetAngleRing1(G4double a)    { fAngleRing1 = a; }
    void SetNDetPerRing(G4int n)      { fNDetPerRing = n; }
    void SetUseDipole(G4bool b)       { fUseDipole = b; }
    void SetUseNEBULA(G4bool b)       { fUseNEBULA = b; }

  private:
    void DefineMaterials();

    PolarimeterDetectorConstructionMessenger* fMessenger;

    // Geometry parameters
    G4double fTargetDistance;  // target-to-polarimeter front face distance
    G4double fAngleRing0;     // scattering angle for ring 0
    G4double fAngleRing1;     // scattering angle for ring 1
    G4int    fNDetPerRing;    // number of detectors per ring

    // Optional components
    G4bool fUseDipole;
    G4bool fUseNEBULA;

    // Logical volumes needed for SD assignment
    G4LogicalVolume* fPolarimeterScinLogical;
};

#endif
