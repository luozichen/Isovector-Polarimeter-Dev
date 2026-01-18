#include "DET01Hit.hh"

G4ThreadLocal G4Allocator<DET01Hit>* DET01HitAllocator = 0;

DET01Hit::DET01Hit()

 : G4VHit(),

   fTime(0.),

   fDetID(-1),

   fEdep(0.)

{}

DET01Hit::DET01Hit(const DET01Hit& right)
 : G4VHit()
{
  fTime = right.fTime;
}

DET01Hit::~DET01Hit() {}

const DET01Hit& DET01Hit::operator=(const DET01Hit& right)
{
  fTime = right.fTime;
  return *this;
}

G4bool DET01Hit::operator==(const DET01Hit& right) const
{
  return (this==&right) ? true : false;
}

void DET01Hit::Draw() {}

void DET01Hit::Print() {}
