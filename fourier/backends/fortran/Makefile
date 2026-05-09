# Makefile - lege-artis/fourier - Fortran backend (v0.1.0 reference)
#
# Per WORKING-SPEC-v0.3-EN.md section 4.1: canonical reference compiled with
# clarity-first flags (-O0, -fcheck=all, -Wall) - no optimisation. Stage 5
# (v0.5+) introduces a separate optimised build target.
#
# Compile:  make
# Test:     make test
# Clean:    make clean
#
# License: Apache 2.0 (this Makefile is code, not docs).

# FC := gfortran (force-assign, ignore Make's built-in FC=f77 default).
# Use FC=ifort or other on the command line if you want to override:
#   make FC=ifort test
FC := gfortran

# Reference (v0.1.0) - clarity flags
FFLAGS_REF  = -O0 -g -fcheck=all -Wall -Wextra -pedantic -std=f2018 -fimplicit-none
FFLAGS_REF += -ffp-contract=off    # no FMA contraction; reproducible IEEE 754

# Performance build (v0.5+) - wired but not used in v0.1.0
FFLAGS_PERF = -O3 -march=native -funroll-loops -std=f2018 -fimplicit-none

# Default to reference build
FFLAGS = $(FFLAGS_REF)

SRC_DIR   = src
TEST_DIR  = tests
BUILD_DIR = build

# OS-aware shell helpers. GNU Make on Windows defaults to cmd.exe, whose
# BUILT-IN `mkdir` rejects `-p` (and shadows any rm-style mkdir found on
# PATH). Detect Windows via the OS env var (set to "Windows_NT" by the OS
# itself) and emit the cmd.exe idiom; POSIX keeps the canonical form.
# `rm -rf` works on Pete's box because rm is NOT a cmd.exe builtin, so
# PATH lookup finds rm.exe (Git-for-Windows / MSYS2 / w64devkit). For
# robustness across stripped Windows installs we still emit the cmd
# equivalent under Windows.
ifeq ($(OS),Windows_NT)
    MKDIR_BUILD = if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)"
    RM_BUILD    = if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
else
    MKDIR_BUILD = mkdir -p "$(BUILD_DIR)"
    RM_BUILD    = rm -rf "$(BUILD_DIR)"
endif

SOURCES   = $(SRC_DIR)/dft_kernel.f90
OBJECTS   = $(BUILD_DIR)/dft_kernel.o
MODULES   = $(BUILD_DIR)/lege_artis_fourier_dft.mod

TESTS     = $(TEST_DIR)/test_dft_unit.f90
TEST_BIN  = $(BUILD_DIR)/test_dft_unit

# ─── Job-3 — Golden-vector tests ──────────────────────────────────────────────
# Per _specs/SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md section 4.
# json_to_fortran_data.py reads shared/golden-vectors/dft_n=*.json and emits
# build/golden/dft_n_<N>.dat files in a Fortran list-directed-read format.
# test_dft_golden.f90 reads those .dat files and verifies dft(input) matches
# the oracle output at 1e-13 max-abs-error.
#
# Python interpreter detection — Windows ships `python`; POSIX ships `python3`.
# Override at the command line if needed:  make PYTHON=python golden-data
ifeq ($(OS),Windows_NT)
    PYTHON ?= python
else
    PYTHON ?= python3
endif

JSON_TO_FORTRAN  = ../../tools/json_to_fortran_data.py
GOLDEN_JSONS     = $(wildcard ../../shared/golden-vectors/dft_n=*.json)
GOLDEN_DAT_DIR   = $(BUILD_DIR)/golden

TESTS_GOLDEN     = $(TEST_DIR)/test_dft_golden.f90
TEST_GOLDEN_BIN  = $(BUILD_DIR)/test_dft_golden

.PHONY: all test perf clean golden-data

all: $(TEST_BIN) $(TEST_GOLDEN_BIN)

$(BUILD_DIR):
	$(MKDIR_BUILD)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.f90 | $(BUILD_DIR)
	$(FC) $(FFLAGS) -c -J$(BUILD_DIR) -o $@ $<

$(TEST_BIN): $(OBJECTS) $(TESTS) | $(BUILD_DIR)
	$(FC) $(FFLAGS) -I$(BUILD_DIR) -o $@ $(OBJECTS) $(TESTS)

# Regenerate .dat files from JSON oracles. Phony — always re-runs the Python
# tool when invoked (the tool is fast + idempotent). Used as an order-only
# prerequisite of $(TEST_GOLDEN_BIN) so the binary itself is not forced to
# rebuild every run.
golden-data: $(JSON_TO_FORTRAN) $(GOLDEN_JSONS) | $(BUILD_DIR)
	$(PYTHON) $(JSON_TO_FORTRAN)

$(TEST_GOLDEN_BIN): $(OBJECTS) $(TESTS_GOLDEN) | $(BUILD_DIR) golden-data
	$(FC) $(FFLAGS) -I$(BUILD_DIR) -o $@ $(OBJECTS) $(TESTS_GOLDEN)

test: $(TEST_BIN) $(TEST_GOLDEN_BIN)
	@echo "Running DFT unit tests (v0.1.0 reference)..."
	@$(TEST_BIN)
	@echo "Running DFT golden-vector tests (v0.1.0-rc Job-3)..."
	@$(TEST_GOLDEN_BIN)

# Performance build — Stage 5 / v0.5+; reuses sources, swaps flags.
# Output binary suffix '_perf' to keep reference / perf builds distinguishable.
perf: FFLAGS = $(FFLAGS_PERF)
perf: $(BUILD_DIR)
	$(FC) $(FFLAGS) -J$(BUILD_DIR) -c -o $(BUILD_DIR)/dft_kernel_perf.o $(SRC_DIR)/dft_kernel.f90
	$(FC) $(FFLAGS) -I$(BUILD_DIR) -o $(BUILD_DIR)/test_dft_unit_perf $(BUILD_DIR)/dft_kernel_perf.o $(TESTS)
	@echo [perf build] $(BUILD_DIR)/test_dft_unit_perf - Stage 5 v0.5+ scope

clean:
	$(RM_BUILD)
