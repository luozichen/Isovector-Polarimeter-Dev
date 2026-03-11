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

# smg4lib include paths
CPPFLAGS += -I$(G4SMACTIONDIR)/include
CPPFLAGS += -I$(G4SMCONSTRUCTIONDIR)/include
CPPFLAGS += -I$(G4SMDATADIR)/sources/include
CPPFLAGS += -I$(G4SMPHYSICSDIR)/include

# smg4lib libraries (all in G4SMLIBDIR/lib)
EXTRALIBS += -L$(G4SMLIBDIR)/lib $(G4SMLDLIBS)

# ROOT
CPPFLAGS += $(shell root-config --cflags)
EXTRALIBS += $(shell root-config --libs)

# Add ANAROOT Support with corrected library names
CPPFLAGS  += -I$(TARTSYS)/include
EXTRALIBS += -L$(TARTSYS)/lib -lanaroot -lananadeko -lanacore -lanacatana -lanadali -lanasamurai -lanaloop -lXMLParser -lXMLIO

.PHONY: all
all: lib bin

include $(G4INSTALL)/config/binmake.gmk
