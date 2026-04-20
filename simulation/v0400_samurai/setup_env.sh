#!/usr/bin/env bash
# shellcheck shell=bash
#
# Environment bootstrap for v0400_samurai on enpg-like hosts.
# Usage:
#   source simulation/v0400_samurai/setup_env.sh
#   # optional overrides:
#   SMSIMDIR=/path/to/smsimulator5.5 GEANT4MAKE_SH=/path/to/geant4make.sh source .../setup_env.sh

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: This script must be sourced, not executed." >&2
  echo "Run: source ${0}" >&2
  exit 1
fi

# Preferred explicit override, then conventional install path.
: "${SMSIMDIR:=/data4/luozc25/files/smsimulator5.5}"

if [[ ! -d "${SMSIMDIR}" ]]; then
  echo "ERROR: SMSIMDIR does not exist: ${SMSIMDIR}" >&2
  return 1
fi

# Find geant4make.sh robustly (legacy and modern layouts).
if [[ -n "${GEANT4MAKE_SH:-}" ]]; then
  _g4_candidates=("${GEANT4MAKE_SH}")
else
  _g4_candidates=(
    "${SMSIMDIR}/../geant4-11.1.2/install/share/Geant4/geant4make/geant4make.sh"
    "/data4/luozc25/files/geant4-11.1.2/install/share/Geant4/geant4make/geant4make.sh"
    "/usr/local/lib64/geant4.10.05.p01/share/Geant4-10.5.1/geant4make/geant4make.sh"
  )
fi

GEANT4MAKE_SH=""
for _candidate in "${_g4_candidates[@]}"; do
  if [[ -f "${_candidate}" ]]; then
    GEANT4MAKE_SH="${_candidate}"
    break
  fi
done

if [[ -z "${GEANT4MAKE_SH}" ]]; then
  echo "ERROR: geant4make.sh not found." >&2
  echo "Tried:" >&2
  for _candidate in "${_g4_candidates[@]}"; do
    echo "  - ${_candidate}" >&2
  done
  echo "Set GEANT4MAKE_SH to your install path and source again." >&2
  return 1
fi

# shellcheck disable=SC1090
source "${GEANT4MAKE_SH}"

# smsimulator/smg4lib variables expected by GNUmakefiles.
export SMSIMDIR
export SMSIMULATOR="${SMSIMDIR}"
export G4SMLIBDIR="${SMSIMDIR}/smg4lib"
export G4SMACTIONDIR="${G4SMLIBDIR}/action"
export G4SMCONSTRUCTIONDIR="${G4SMLIBDIR}/construction"
export G4SMDATADIR="${G4SMLIBDIR}/data"
export G4SMPHYSICSDIR="${G4SMLIBDIR}/physics"

_prepend_path_once() {
  local _var_name="$1"
  local _value="$2"

  [[ -n "${_value}" ]] || return 0
  [[ -d "${_value}" ]] || return 0

  local _current="${!_var_name:-}"
  case ":${_current}:" in
    *":${_value}:"*) ;;
    *)
      if [[ -n "${_current}" ]]; then
        export "${_var_name}=${_value}:${_current}"
      else
        export "${_var_name}=${_value}"
      fi
      ;;
  esac
}

# Keep PATH/LD_LIBRARY_PATH clean and idempotent across repeated sourcing.
_prepend_path_once PATH "${SMSIMDIR}/bin/Linux-g++"
_prepend_path_once LD_LIBRARY_PATH "${G4SMLIBDIR}/lib"
_prepend_path_once LD_LIBRARY_PATH "${SMSIMDIR}/lib"

# Root, if present in the known local tree.
if [[ -x "${SMSIMDIR}/../root-6.30.04/install/bin/thisroot.sh" ]]; then
  # shellcheck disable=SC1091
  source "${SMSIMDIR}/../root-6.30.04/install/bin/thisroot.sh"
fi

unset _candidate
unset _g4_candidates

echo "[setup_env] GEANT4MAKE_SH=${GEANT4MAKE_SH}"
echo "[setup_env] SMSIMDIR=${SMSIMDIR}"
echo "[setup_env] G4SMLIBDIR=${G4SMLIBDIR}"
