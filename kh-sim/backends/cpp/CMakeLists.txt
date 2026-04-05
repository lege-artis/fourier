# KH-SIM C++ backend — Task KH-005
# Requirements: CMake 3.20+, C++20 compiler (MSVC 19.29+ / GCC 11+ / Clang 13+)
# All dependencies fetched automatically via FetchContent (no vcpkg required).

cmake_minimum_required(VERSION 3.20)
project(kh-sim-cpp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ── Compiler flags ────────────────────────────────────────────────────────────
if(MSVC)
  add_compile_options(/W3 /O2 /EHsc)
  # Suppress cpp-httplib MSVC warnings
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS NOMINMAX WIN32_LEAN_AND_MEAN)
else()
  add_compile_options(-Wall -O2)
endif()

# ── Dependencies via FetchContent ─────────────────────────────────────────────
include(FetchContent)

# cpp-httplib — header-only HTTP server/client
FetchContent_Declare(
  httplib
  GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
  GIT_TAG        v0.18.1
  GIT_SHALLOW    TRUE
)

# nlohmann/json — header-only JSON
FetchContent_Declare(
  nlohmann_json
  GIT_REPOSITORY https://github.com/nlohmann/json.git
  GIT_TAG        v3.11.3
  GIT_SHALLOW    TRUE
)

FetchContent_MakeAvailable(httplib nlohmann_json)

# ── Main server executable ────────────────────────────────────────────────────
add_executable(kh-sim-cpp
  src/main.cpp
  src/physics.cpp
)

target_include_directories(kh-sim-cpp PRIVATE src)

target_link_libraries(kh-sim-cpp PRIVATE
  httplib::httplib
  nlohmann_json::nlohmann_json
)

# Windows: link WinSock (required by cpp-httplib)
if(WIN32)
  target_link_libraries(kh-sim-cpp PRIVATE ws2_32)
endif()

# ── Validation test executable ────────────────────────────────────────────────
# Guarded: Docker build context only contains src/; tests/ is host-only.
# EXISTS check prevents CMake generate failure when tests/ is absent (Docker).
# CTest still runs normally on host where tests/validation_test.cpp is present.
enable_testing()
if(EXISTS "${CMAKE_SOURCE_DIR}/tests/validation_test.cpp")
  add_executable(kh-sim-cpp-validate
    tests/validation_test.cpp
    src/physics.cpp
  )
  target_include_directories(kh-sim-cpp-validate PRIVATE src)
  target_link_libraries(kh-sim-cpp-validate PRIVATE nlohmann_json::nlohmann_json)

  add_test(
    NAME validation
    COMMAND kh-sim-cpp-validate
            "${CMAKE_SOURCE_DIR}/../../shared/physics/kh_reference_output.json"
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  )
endif()
