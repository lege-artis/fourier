# Makefile - lege-artis/fourier - C++ backend (v0.2.0 reference)
#
# Mirrors backends/fortran/Makefile structure. Per WORKING-SPEC-v0.3-EN.md
# section 4: canonical reference compiled with clarity-first flags
# (-O0, -Wall, -Wpedantic, -ffp-contract=off) - no optimisation. Stage 5
# (v0.5+) introduces a separate optimised build target.
#
# Compile:  make
# Test:     make test
# Clean:    make clean
#
# License: Apache 2.0

# CXX := g++ (force-assign; ignore Make's built-in CXX=c++ which can vary).
# Use CXX=clang++ on the command line to override:
#   make CXX=clang++ test
CXX := g++

# Reference (v0.2.0) - clarity flags, IEEE 754 strict
CXXFLAGS_REF  = -O0 -g -Wall -Wextra -Wpedantic -std=c++17
CXXFLAGS_REF += -ffp-contract=off

# Performance build (v0.5+) - wired but not used in v0.2.0
CXXFLAGS_PERF = -O3 -march=native -funroll-loops -std=c++17

# Default to reference build
CXXFLAGS = $(CXXFLAGS_REF)

INC_DIR   = include
SRC_DIR   = src
TEST_DIR  = tests
BUILD_DIR = build

# OS-aware shell helpers (KB-038). GNU Make on Windows defaults to cmd.exe
# whose built-in mkdir rejects -p; use OS-aware pattern.
ifeq ($(OS),Windows_NT)
    MKDIR_BUILD       = if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)"
    MKDIR_GOLDEN      = if not exist "$(BUILD_DIR)\golden" mkdir "$(BUILD_DIR)\golden"
    RM_BUILD          = if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
else
    MKDIR_BUILD       = mkdir -p "$(BUILD_DIR)"
    MKDIR_GOLDEN      = mkdir -p "$(BUILD_DIR)/golden"
    RM_BUILD          = rm -rf "$(BUILD_DIR)"
endif

INCLUDES  = -I$(INC_DIR) -I$(TEST_DIR)

KERNEL_SRC = $(SRC_DIR)/dft_kernel.cpp
KERNEL_OBJ = $(BUILD_DIR)/dft_kernel.o

TEST_UNIT_SRC      = $(TEST_DIR)/test_dft_unit.cpp
TEST_PROPERTY_SRC  = $(TEST_DIR)/test_dft_property.cpp
TEST_PHYSICS_SRC   = $(TEST_DIR)/test_dft_physics.cpp
TEST_GOLDEN_SRC    = $(TEST_DIR)/test_dft_golden.cpp

TEST_UNIT_BIN      = $(BUILD_DIR)/test_dft_unit
TEST_PROPERTY_BIN  = $(BUILD_DIR)/test_dft_property
TEST_PHYSICS_BIN   = $(BUILD_DIR)/test_dft_physics
TEST_GOLDEN_BIN    = $(BUILD_DIR)/test_dft_golden

ALL_TEST_BINS = $(TEST_UNIT_BIN) $(TEST_PROPERTY_BIN) $(TEST_PHYSICS_BIN) $(TEST_GOLDEN_BIN)

.PHONY: all test perf clean golden-data

all: $(ALL_TEST_BINS)

$(BUILD_DIR):
	$(MKDIR_BUILD)

# -- Golden-vector data prep --------------------------------------------------
# Generate build/golden/dft_n_*.dat from shared/golden-vectors/*.json via the
# shared cross-language converter (tools/json_to_fortran_data.py).
# Both Fortran and C++ backends consume identical .dat artifacts.
golden-data: | $(BUILD_DIR)
	$(MKDIR_GOLDEN)
	python ../../tools/json_to_fortran_data.py

# -- Kernel object ------------------------------------------------------------
$(KERNEL_OBJ): $(KERNEL_SRC) $(INC_DIR)/lege_artis_fourier/dft_kernel.hpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c -o $@ $(KERNEL_SRC)

# -- Test binaries ------------------------------------------------------------
$(TEST_UNIT_BIN): $(KERNEL_OBJ) $(TEST_UNIT_SRC) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(KERNEL_OBJ) $(TEST_UNIT_SRC)

$(TEST_PROPERTY_BIN): $(KERNEL_OBJ) $(TEST_PROPERTY_SRC) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(KERNEL_OBJ) $(TEST_PROPERTY_SRC)

$(TEST_PHYSICS_BIN): $(KERNEL_OBJ) $(TEST_PHYSICS_SRC) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(KERNEL_OBJ) $(TEST_PHYSICS_SRC)

$(TEST_GOLDEN_BIN): $(KERNEL_OBJ) $(TEST_GOLDEN_SRC) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(KERNEL_OBJ) $(TEST_GOLDEN_SRC)

# -- Run all tests ------------------------------------------------------------
test: $(ALL_TEST_BINS) golden-data
	@echo Running DFT unit tests (v0.2.0 C++ ref)...
	@$(TEST_UNIT_BIN)
	@echo Running DFT property tests (v0.2.0 C++ ref)...
	@$(TEST_PROPERTY_BIN)
	@echo Running DFT physics testbeds (v0.2.0 C++ ref)...
	@$(TEST_PHYSICS_BIN)
	@echo Running DFT golden-vector verification (v0.2.0 C++ ref)...
	@$(TEST_GOLDEN_BIN)

# -- Performance build (Stage 5 / v0.5+; wired but not exercised) -------------
perf: CXXFLAGS = $(CXXFLAGS_PERF)
perf: $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c -o $(BUILD_DIR)/dft_kernel_perf.o $(KERNEL_SRC)
	@echo [perf build] $(BUILD_DIR)/dft_kernel_perf.o - Stage 5 v0.5+ scope

clean:
	$(RM_BUILD)
