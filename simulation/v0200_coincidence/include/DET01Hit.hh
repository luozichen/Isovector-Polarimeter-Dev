#ifndef DET01Hit_h
#define DET01Hit_h 1

#include "G4VHit.hh"
#include "G4THitsCollection.hh"
#include "G4Allocator.hh"
#include "G4ThreeVector.hh"

class DET01Hit : public G4VHit
{
  public:
    DET01Hit();
    DET01Hit(const DET01Hit&);
    virtual ~DET01Hit();

    const DET01Hit& operator=(const DET01Hit&);
    G4bool operator==(const DET01Hit&) const;

    inline void* operator new(size_t);
    inline void  operator delete(void*);

    virtual void Draw();
    virtual void Print();

    // Setters/Getters
    void SetTime(G4double t) { fTime = t; };
    G4double GetTime() const { return fTime; };

    void SetDetID(G4int id) { fDetID = id; };
    G4int GetDetID() const { return fDetID; };

    void SetEdep(G4double de) { fEdep = de; };
    void AddEdep(G4double de) { fEdep += de; };
    G4double GetEdep() const { return fEdep; };

    void SetPosIn(G4ThreeVector xyz) { fPosIn = xyz; };
    G4ThreeVector GetPosIn() const { return fPosIn; };

    void SetPosOut(G4ThreeVector xyz) { fPosOut = xyz; };
    G4ThreeVector GetPosOut() const { return fPosOut; };

    void SetHasPrimary(G4bool b) { fHasPrimary = b; };
    G4bool GetHasPrimary() const { return fHasPrimary; };

  private:
    G4double fTime;
    G4int fDetID;
    G4double fEdep;
    G4ThreeVector fPosIn;
    G4ThreeVector fPosOut;
    G4bool fHasPrimary;
};

typedef G4THitsCollection<DET01Hit> DET01HitsCollection;

extern G4ThreadLocal G4Allocator<DET01Hit>* DET01HitAllocator;

inline void* DET01Hit::operator new(size_t)
{
  if(!DET01HitAllocator)
      DET01HitAllocator = new G4Allocator<DET01Hit>;
  return (void *) DET01HitAllocator->MallocSingle();
}

inline void DET01Hit::operator delete(void *hit)
{
  DET01HitAllocator->FreeSingle((DET01Hit*) hit);
}

#endif
