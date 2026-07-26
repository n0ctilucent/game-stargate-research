#!/usr/bin/env bash
#
# bitsmasher-stargate bootstrap script
# Role: Control Plane, Model Registry, & Vertex AI Gateway
#
# SPDX-FileCopyrightText: ©2025 franklin <smoooth.y62wj@passmail.net>
# SPDX-License-Identifier: MIT

# ChangeLog:
# v0.1 02/25/2025 initial version
# v0.2 05/09/2026 Stargate split: Added LFS hydration and Pandas/Registry init

# Stargate-specific dependencies
# git-lfs: Binary transit
# python3-pandas/pyarrow: Parquet-backed Registry
# python3-networkx: Topological analysis
# python3-google-cloud-aiplatform: Vertex AI Bridge
DEB_PKG=(git git-lfs git-delta gnupg pass python3-pandas python3-pyarrow python3-networkx python3-pip python3-pytest)
LRED='\033[1;31m'
LGREEN='\033[0;32m'
NC='\033[0m'

function hydrate_lfs() {
    log_header "# --- Git LFS Hydration -----------------------------------------------"
    if ! git lfs version >/dev/null 2>&1; then
        log_error "git-lfs not installed. Skipping hydration."
        return 1
    fi

    log_info "Fetching heavy binaries and registry state..."
    git lfs pull || { log_error "LFS pull failed. Check mdt-keymaster SSH status."; exit 1; }
    log_info "LFS Hydration complete."
}

function init_registry() {
    log_header "# --- Model Registry Initialization -----------------------------------"
    if [ ! -f "registry.parquet" ]; then
        log_warn "registry.parquet not found. Initializing new Stargate Registry..."
        # Trigger the python script to create the initial dataframe structure
        python3 src/stargate/registry.py --init-only
        log_info "Registry initialized."
    else
        log_info "Found existing Registry: $(du -h registry.parquet | awk '{print $1}')"
    fi
}

function required_files() {
  log_header "# --- Check GNU Autotools files ----------------------------------------"
  local files=("AUTHORS" "ChangeLog" "NEWS")
  for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
      log_info "Creating required file ${file} as symlink to README.md"
      ln -sf README.md "$file"
    fi
  done
}

function run_aclocal() {
  log_header "# --- Running aclocal -------------------------------------------------"
  AUTOCONF_VERSION=2.71 AUTOMAKE_VERSION=1.16 aclocal || exit 1
  log_info ".. done with aclocal."
}

function run_autoconf() {
  log_header "# --- Running autoconf ------------------------------------------------"
  log_info "Running autoreconf..."
  autoreconf -fi || exit 1
  log_info "... done with autoconf."
}

function run_automake() {
  log_header "# --- Running automake ------------------------------------------------"
  log_info "Running automake..."
  automake -a -c --add-missing || exit 1
  log_info "... done with automake."
}

function main() {
  # Visual Branding
  if [ -d "${HOME}/workspace/fonts/figlet" ] && command -v figlet >/dev/null; then
    echo -ne "${LGREEN}"
    figlet -f "${HOME}/workspace/fonts/figlet/pagga" "STARGATE CP"
    echo -ne "${NC}\n"
  fi
  
  # Source common bitsmasher functions
  if [ -f "bin/common.sh" ]; then
    source "bin/common.sh"
  else
    echo -e "${LRED}Critical: bin/common.sh is missing. Is this the bitsmasher-stargate repo?${NC}"
    exit 1
  fi

  log_info "Stargate Control Plane environment detected."


  # 2. Registry Check
  init_registry

  # 3. Autotools Bootstrap
  if [ ! -d "aclocal" ]; then mkdir -p aclocal; fi

  if [ ! -f "Makefile.in" ] && [ -f "./config.status" ]; then
    rm config.status
    log_warn "Makefile.in is missing: erasing stale config.status"
  fi

  required_files
  run_aclocal
  run_autoconf
  run_automake

  log_header "# --- Configuration ---------------------------------------------------"
  ./configure || { log_error "Configure failed. Check config.log"; exit 1; }
  
  log_info "STARGATE setup complete. Ready for Vertex AI handshake."
}

main "$@"
