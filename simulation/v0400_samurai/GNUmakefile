# ============================================================
# GNUmakefile for sim_polarimeter
# Follows smsimulator5.5 build conventions
#
# Environment variables (set by smsimulator5.5/setup.sh):
#   SMSIMDIR, G4SMLIBDIR, G4SMACTIONDIR, G4SMCONSTRUCTIONDIR,
#   G4SMDATADIR, G4SMPHYSICSDIR, G4INSTALL
# ============================================================

name := sim_polarimeter

G4TARGET := $(name)
G4EXLIB := true

# Force Qt support
#G4UI_USE_QT = 1
#G4VIS_USE_QT = 1
#G4VIS_BUILD_QT_DRIVER = 1

# smg4lib include paths
CPPFLAGS += -I$(G4SMACTIONDIR)/include
CPPFLAGS += -I$(G4SMCONSTRUCTIONDIR)/include
CPPFLAGS += -I$(G4SMDATADIR)/sources/include
CPPFLAGS += -I$(G4SMPHYSICSDIR)/include

# smg4lib libraries (all in G4SMLIBDIR/lib)
EXTRALIBS += -L$(G4SMLIBDIR)/lib $(G4SMLDLIBS)
# Fallback explicit ordering for static-link environments where
# transitive deps are not auto-resolved (e.g. libsmaction ->
# libsmdata symbols such as SimDataManager / TRunSimParameter).
EXTRALIBS += -lsmaction -lsmconstruction -lsmphysics -lsmdata
# Legacy Geant4 static builds can miss physics-list symbols unless
# all granular archives are available to the linker.
EXTRALIBS += $(wildcard $(G4INSTALL)/lib/$(G4SYSTEM)/libG4*.a)

# ROOT
CPPFLAGS += $(shell root-config --cflags)
EXTRALIBS += $(shell root-config --libs)

# Add ANAROOT Support with corrected library names
CPPFLAGS  += -I$(TARTSYS)/include
EXTRALIBS += -L$(TARTSYS)/lib -lanaroot -lananadeko -lanacore -lanacatana -lanadali -lanasamurai -lanaloop -lXMLParser -lXMLIO

.PHONY: all
all: lib bin

include $(G4INSTALL)/config/binmake.gmk
