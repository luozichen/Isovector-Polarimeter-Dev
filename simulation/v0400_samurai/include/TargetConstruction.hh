#ifndef TargetConstruction_h
#define TargetConstruction_h 1

#include "globals.hh"

class G4LogicalVolume;

// Simple CH2 target construction.
// Creates a polyethylene slab at the origin.

class TargetConstruction
{
  public:
    TargetConstruction();
    virtual ~TargetConstruction();

    G4LogicalVolume* ConstructSub();

    void SetTargetSizeX(G4double x) { fSizeX = x; }
    void SetTargetSizeY(G4double y) { fSizeY = y; }
    void SetTargetSizeZ(G4double z) { fSizeZ = z; }

  private:
    G4double fSizeX;  // default: 5 cm
    G4double fSizeY;  // default: 5 cm
    G4double fSizeZ;  // default: 1 cm
};

#endif
