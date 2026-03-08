#ifndef DET01DetectorConstruction_h
#define DET01DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class G4VPhysicalVolume;
class G4LogicalVolume;

class DET01DetectorConstruction : public G4VUserDetectorConstruction
{
  public:
    DET01DetectorConstruction();
    virtual ~DET01DetectorConstruction();

    virtual G4VPhysicalVolume* Construct();
    virtual void ConstructSDandField();

  private:
    void DefineMaterials();

    // Logical volumes needed for SD
    G4LogicalVolume* fPhotocathodeLogical;
};

#endif
