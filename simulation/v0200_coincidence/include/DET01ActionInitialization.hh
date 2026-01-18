#ifndef DET01ActionInitialization_h
#define DET01ActionInitialization_h 1

#include "G4VUserActionInitialization.hh"

class DET01ActionInitialization : public G4VUserActionInitialization
{
  public:
    DET01ActionInitialization();
    virtual ~DET01ActionInitialization();

    virtual void BuildForMaster() const;
    virtual void Build() const;
};

#endif
