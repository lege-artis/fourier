# JOB-2 — Pascal port of the canonical DFT kernel

**Status:** Ready to execute. Depends only on Fortran reference + C++ port + canonical equations doc.
**Estimated effort:** 4-6 hours (kernel ~45 min; 4 test programs ~3-4 h; cross-language verify ~1 h; complex-record idioms add ~30 min over what Rust would have taken).
**Acceptance gate:** all 4 test suites green at the locked tolerance gates, with bit-identical worst-error numbers vs Fortran reference + C++ port.

---

## §1. The brief

Port the canonical DFT kernel — `X[k] = sum_{n=0}^{N-1} x[n] * exp(-2j*pi*k*n/N)` — to Free Pascal (FPC), mirroring the proven C++ port structure under `backends/cpp/`. Produce 4 test programs (unit, property, physics, golden) that pass at the same tolerance gates as Fortran + C++.

**Why Pascal first** (and not Rust):
- **Numerical Recipes 1986 (Pascal edition)** is a real historical anchor. The implementation style — explicit indexing, no operator overloading for complex math, named record types — is what Press/Teukolsky/Vetterling/Flannery actually wrote. Mirroring it gives the project an honest tie to that lineage that Rust cannot offer.
- **Third independent linguistic translation.** Pascal's syntax and idiom set is far enough from Fortran (no array semantics) AND far enough from C++ (no templates / operator overloading / namespaces) that getting bit-identical numerics out of all three is strong evidence the canonical equation translates faithfully across language paradigms — not just an artifact of one compiler family.
- **Cross-check value for the Rust round.** When Rust lands in v0.2.2, having Pascal numbers already in the cross-language baseline makes the Rust verification a 3-way comparison (Fortran ⟷ C++ ⟷ Pascal ⟷ Rust), which is stronger than the current 2-way (Fortran ⟷ C++) extended by one.

**Locked priors:**
- The Fortran reference at `backends/fortran/src/dft_kernel.f90` is the empirical anchor.
- The C++ port at `backends/cpp/src/dft_kernel.cpp` produced bit-identical worst-error numbers to Fortran. Same gates.
- Pascal must do the same. **Bit-identical** in IEEE-754 sense; see §3.

### 1.1 Implementation discipline (Pascal-specific)

All §1 rules from `_specs/SONNET-HANDOFF-v0.2.0-CPP-PORT.md` apply. Pascal-specific adaptations:

- **Free Pascal Compiler (FPC) 3.2.2 or later.** This is the standard open-source Pascal compiler — universally available on macOS / Linux / Windows. **No Delphi-specific extensions.** No `{$mode delphi}` directive — use default `{$mode objfpc}` or `{$mode fpc}` for the kernel + tests.
- **`Double` type for all real numbers.** This is FPC's IEEE-754 double-precision. `Real` is also acceptable (alias for `Double` in objfpc/fpc modes on modern targets).
- **No external libraries beyond FPC stdlib.** Specifically: `SysUtils`, `Math`, and (for golden-vector loading) `fpjson` + `jsonparser`. All ship with FPC by default. **NO** third-party FFT libraries. The Pascal port is a reference implementation of Eq. DFT-1, same as Fortran + C++ kernels.
- **Complex numbers as a record type.** FPC's `ucomplex` unit exists but is awkward and operator-overload-style. **Use a named record:**
  ```pascal
  type
    TComplex = record
      re: Double;
      im: Double;
    end;
    TComplexArray = array of TComplex;
  ```
  Implement `complex_add`, `complex_mul`, `complex_from_polar(r, theta)`, `complex_abs` as plain functions taking/returning `TComplex`. This is what Numerical Recipes 1986 actually does, and it makes the math read explicitly in code.
- **Module layout:**
  ```
  backends/pascal/
  ├── Makefile                       (fpc invocations, OS-aware)
  ├── src/
  │   └── dft_kernel.pas             (unit DftKernel; interface + implementation)
  └── tests/
      ├── test_dft_unit.pas          (program test_dft_unit; 5 tests; gate 1e-13)
      ├── test_dft_property.pas      (6 property tests; gate 1e-13, P8 9.1e-13)
      ├── test_dft_physics.pas       (14 physics testbed tests; gate 1e-13, PT-DFT-03B 1e-10)
      └── test_dft_golden.pas        (golden-vector loader + verification; gate Option G 1e-13*sqrt(N))
  ```
- **Public API** in `unit DftKernel` (Pascal has no separate `.h` — interface block is the equivalent):
  ```pascal
  unit DftKernel;

  {$mode objfpc}{$H+}

  interface

  type
    TComplex = record
      re: Double;
      im: Double;
    end;
    TComplexArray = array of TComplex;

  { Direct DFT: X[k] = sum_{n=0..N-1} x[n] * exp(-2*pi*j*k*n/N) }
  procedure Dft(const x: TComplexArray; out big_x: TComplexArray);

  { Inverse DFT: x[n] = (1/N) * sum_{k=0..N-1} X[k] * exp(+2*pi*j*k*n/N) }
  procedure Idft(const big_x: TComplexArray; out x: TComplexArray);

  { Complex helpers used pervasively in tests }
  function ComplexAdd(const a, b: TComplex): TComplex;
  function ComplexMul(const a, b: TComplex): TComplex;
  function ComplexFromPolar(r, theta: Double): TComplex;
  function ComplexAbs(const a: TComplex): Double;

  implementation

  // ...
  end.
  ```
- **Equation-to-code mapping** in `dft_kernel.pas` interface comment block, same convention as `backends/cpp/src/dft_kernel.cpp` header.
- **Wrong-size inputs:** use `Assert(Length(x) > 0)` at the top of `Dft` / `Idft`. FPC's `Assert` is compile-time toggled by `{$ASSERTIONS ON/OFF}` directive — leave assertions ON for reference build.
- **ASCII-only.** No Unicode in `.pas` files. KB-039 applies. Pascal's lexer is generally tolerant of high-byte characters in string literals but trips on em-dashes in comments on some Windows code pages. Stick to ASCII.

---

## §2. Tolerance gates (LOCKED — do not change)

Identical to Fortran + C++ gates. These are bit-identity-meaningful; touching them invalidates the cross-language baseline match.

| Test class | Gate | Notes |
|------------|------|-------|
| Unit (5 tests) | 1e-13 | DC, Nyquist, complex unit, linearity, parseval |
| Property (6 tests) | 1e-13 (P1-P7); **P8 = 9.1e-13** | P8's tighter empirical bound documented in KB-040 |
| Physics (14 tests) | 1e-13 (PT-DFT-01/02/03A); **PT-DFT-03B = 1e-10** | PT-DFT-03B has a justified weaker bound |
| Golden vectors (6 JSONs, 748 element-checks) | Option G: `1e-13 * sqrt(N)` per element | Per Higham §4.2 forward-error-bound rationale |

**If a gate fails, re-read your implementation, not the gate.**

---

## §3. Bit-identity cross-language baseline match

**The headline property of the v0.2.x line.** Pascal must produce the same IEEE-754 worst-error numbers as Fortran + C++ for the same input vectors. Bit-identical, not approximately equal.

Why this is achievable in Pascal — same as the C++ port argument:

- FPC uses platform `Double` which is IEEE-754 binary64 on all supported targets.
- FPC's `Cos` / `Sin` (from the `Math` unit) wrap the C runtime's `cos` / `sin` — same routines Fortran and C++ use.
- FPC does **not** auto-FMA. The default code generator emits separate `mul` and `add` instructions, matching Fortran's `-ffp-contract=off` behaviour and C++'s `-ffp-contract=off`.
- Accumulation order is explicit because Pascal has no auto-vectorization at `-O1`/`-O2` and Eq. DFT-1 is a simple sequential `for` loop.

**Inner-loop shape — non-negotiable:**

```pascal
function DftSingleBin(const x: TComplexArray; k: Integer): TComplex;
var
  n, big_n: Integer;
  acc, twiddle: TComplex;
  phase: Double;
begin
  big_n := Length(x);
  acc.re := 0.0;
  acc.im := 0.0;
  for n := 0 to big_n - 1 do
  begin
    phase := -2.0 * Pi * k * n / big_n;
    twiddle.re := Cos(phase);
    twiddle.im := Sin(phase);
    acc := ComplexAdd(acc, ComplexMul(x[n], twiddle));
  end;
  Result := acc;
end;
```

This is the **only** acceptable inner-loop shape. Do not reorder. Do not "optimize" by combining `Cos`/`Sin` into a recurrence. Do not vectorize. The point of the reference is bit-reproducibility.

**Verification step at end of JOB-2:**
1. Run Fortran tests, record worst-error numbers per test (already done; values in v0.2.0 release notes).
2. Run C++ tests, confirm match (already done; v0.2.0 shipped this proof).
3. Run Pascal tests, confirm worst-error numbers match Fortran + C++ to within `epsilon(0.0)` (= 4.94e-324 normal-subnormal boundary OR 2.22e-16 = `1.0 - Pred(1.0)`, depending on how you measure — both are "indistinguishable from Fortran" in IEEE-754 terms).

If Pascal differs from Fortran + C++ in any worst-error number by more than 2.22e-16:
- Most likely cause: implicit type promotion in your phase calculation. `-2.0 * Pi * k * n / big_n` — ensure k and n are converted to Double explicitly (`Double(k)` / `Double(n)`) before the multiplication. FPC's integer-arithmetic rules differ from C++'s.
- Second: `ComplexMul` implementation. The standard `(a+bi)(c+di) = (ac-bd) + (ad+bc)i` formula has TWO valid evaluation orders depending on parenthesization. Force the same order as Fortran and C++:
  ```pascal
  function ComplexMul(const a, b: TComplex): TComplex;
  begin
    Result.re := a.re * b.re - a.im * b.im;
    Result.im := a.re * b.im + a.im * b.re;
  end;
  ```
  This matches both Fortran (`real(z1)*real(z2) - aimag(z1)*aimag(z2)`) and C++ `std::complex` (which follows ISO/IEC 14882 §29.5.7 for the same evaluation order).
- Third: `Cos`/`Sin` differences across FPC targets. FPC on Windows historically wraps `crtdll.cos`; on Linux it wraps `libm`. Both give IEEE-754 correctly-rounded results for `cos`/`sin` to within 1 ULP — but the 1-ULP variance can ripple into a 1e-15 worst-error difference. If you see this, document it in `STATUS-REPORT-FILLED.md` §"Open questions" — Pete will decide whether to weaken Pascal's gate by one ULP or absorb the difference.

---

## §4. Build profile

Same philosophy as Fortran + C++: clarity flags, NOT performance flags. Stage 5 (`-O3`-equivalent + LTO + perf comparisons) is gated v0.5+ and out of scope.

**FPC flags for the reference build:**

```
-O1            (basic optimizations; -O2 starts auto-inlining which complicates equation-to-code mapping)
-gl            (line-info debug data)
-CR            (range checking ON — catches off-by-one in array index loops; reference is correctness-first)
-Sc            (assertions ON; alias for {$ASSERTIONS ON})
-Sa            (assertions are checked; for safety)
-vewn          (verbose: errors + warnings + notes; treat warnings seriously)
```

**Makefile shim** (`backends/pascal/Makefile`):

```make
FPC := fpc

FLAGS_REF := -O1 -gl -CR -Sa -vewn
FLAGS_PERF := -O3 -CX -XX                # v0.5+ Stage 5
FLAGS := $(FLAGS_REF)

SRC_DIR := src
TEST_DIR := tests
BUILD_DIR := build

ifeq ($(OS),Windows_NT)
    MKDIR_BUILD := if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)"
    RM_BUILD := if exist "$(BUILD_DIR)" rmdir /s /q "$(BUILD_DIR)"
    EXE_EXT := .exe
else
    MKDIR_BUILD := mkdir -p "$(BUILD_DIR)"
    RM_BUILD := rm -rf "$(BUILD_DIR)"
    EXE_EXT :=
endif

.PHONY: build test test-unit test-property test-physics test-golden clean

build:
	$(MKDIR_BUILD)
	$(FPC) $(FLAGS) -FU$(BUILD_DIR) -FE$(BUILD_DIR) $(SRC_DIR)/dft_kernel.pas

test: test-unit test-property test-physics test-golden

test-unit: build
	$(FPC) $(FLAGS) -Fu$(BUILD_DIR) -FU$(BUILD_DIR) -FE$(BUILD_DIR) $(TEST_DIR)/test_dft_unit.pas
	$(BUILD_DIR)/test_dft_unit$(EXE_EXT)

test-property: build
	$(FPC) $(FLAGS) -Fu$(BUILD_DIR) -FU$(BUILD_DIR) -FE$(BUILD_DIR) $(TEST_DIR)/test_dft_property.pas
	$(BUILD_DIR)/test_dft_property$(EXE_EXT)

test-physics: build
	$(FPC) $(FLAGS) -Fu$(BUILD_DIR) -FU$(BUILD_DIR) -FE$(BUILD_DIR) $(TEST_DIR)/test_dft_physics.pas
	$(BUILD_DIR)/test_dft_physics$(EXE_EXT)

test-golden: build
	$(FPC) $(FLAGS) -Fu$(BUILD_DIR) -FU$(BUILD_DIR) -FE$(BUILD_DIR) $(TEST_DIR)/test_dft_golden.pas
	$(BUILD_DIR)/test_dft_golden$(EXE_EXT)

clean:
	$(RM_BUILD)
```

OS-awareness pattern explicitly follows KB-038 (cmd.exe `mkdir` doesn't support `-p`).

---

## §5. Test-program structure

Pascal has no built-in unit-test framework comparable to Rust's `#[test]` or C++ Google Test. **Use the same "program with explicit PASS/FAIL print + exit code" pattern that Fortran uses** (per `backends/fortran/tests/test_dft_unit.f90`). Each test program is a standalone `.pas` file with a single `program` block and multiple test procedures.

Skeleton (mirrors `test_dft_unit.f90`):

```pascal
program test_dft_unit;

{$mode objfpc}{$H+}{$ASSERTIONS ON}

uses
  SysUtils, Math, DftKernel;

const
  GATE_UNIT = 1.0e-13;

var
  total: Integer = 0;
  failed: Integer = 0;
  worst_err_overall: Double = 0.0;

procedure AssertComplexClose(const actual, expected: TComplex; tol: Double; const ctx: string);
var
  diff: TComplex;
  err: Double;
begin
  diff.re := actual.re - expected.re;
  diff.im := actual.im - expected.im;
  err := ComplexAbs(diff);
  Inc(total);
  if err > worst_err_overall then worst_err_overall := err;
  if err >= tol then
  begin
    Writeln(Format('  FAIL  %s: err=%.3e gate=%.3e', [ctx, err, tol]));
    Inc(failed);
  end
  else
    Writeln(Format('  pass  %s: err=%.3e', [ctx, err]));
end;

procedure U1_DcInput;
var
  x, big_x: TComplexArray;
  i, big_n: Integer;
  zero, expected: TComplex;
begin
  big_n := 16;
  SetLength(x, big_n);
  for i := 0 to big_n - 1 do
  begin
    x[i].re := 1.0;
    x[i].im := 0.0;
  end;
  Dft(x, big_x);
  expected.re := Double(big_n);
  expected.im := 0.0;
  AssertComplexClose(big_x[0], expected, GATE_UNIT, 'U1.DC.k0');
  zero.re := 0.0; zero.im := 0.0;
  for i := 1 to big_n - 1 do
    AssertComplexClose(big_x[i], zero, GATE_UNIT, Format('U1.DC.k%d', [i]));
end;

// ... U2, U3, U4, U5

procedure WriteBanner;
begin
  Writeln('=========================================================');
  Writeln(' lege-artis/fourier - unit tests (v0.2.1 Pascal ref)');
  Writeln('=========================================================');
end;

procedure WriteFooter;
begin
  Writeln('=========================================================');
  Writeln(Format(' total=%d  failed=%d  worst-err=%.3e', [total, failed, worst_err_overall]));
  Writeln('=========================================================');
end;

begin
  WriteBanner;
  U1_DcInput;
  // U2, U3, U4, U5 calls
  WriteFooter;
  if failed > 0 then
    Halt(1)
  else
    Halt(0);
end.
```

Match the banner / footer / worst-err format to Fortran's exactly — that's what makes the cross-language verification step a `diff` away from confirmation.

---

## §6. Golden-vector loader

Pascal can read JSON via `fpjson` + `jsonparser` (ships with FPC).

```pascal
uses fpjson, jsonparser;

procedure LoadGoldenVector(const path: string; out vec_n: Integer;
                           out vec_input, vec_expected: TComplexArray);
var
  raw: TStringList;
  jdata: TJSONData;
  jobj: TJSONObject;
  jarr_re, jarr_im: TJSONArray;
  i: Integer;
begin
  raw := TStringList.Create;
  try
    raw.LoadFromFile(path);
    jdata := GetJSON(raw.Text);
    try
      jobj := TJSONObject(jdata);
      vec_n := jobj.Integers['n'];
      SetLength(vec_input, vec_n);
      jarr_re := jobj.Arrays['input_re'];
      jarr_im := jobj.Arrays['input_im'];
      for i := 0 to vec_n - 1 do
      begin
        vec_input[i].re := jarr_re.Floats[i];
        vec_input[i].im := jarr_im.Floats[i];
      end;
      SetLength(vec_expected, vec_n);
      jarr_re := jobj.Arrays['expected_re'];
      jarr_im := jobj.Arrays['expected_im'];
      for i := 0 to vec_n - 1 do
      begin
        vec_expected[i].re := jarr_re.Floats[i];
        vec_expected[i].im := jarr_im.Floats[i];
      end;
    finally
      jdata.Free;
    end;
  finally
    raw.Free;
  end;
end;
```

The golden-vector files are at `../../../shared/golden-vectors/golden_*.json` relative to `backends/pascal/tests/`. Use `ExpandFileName` to resolve.

**Per-element error**: report MAX over all N elements of each vector. Gate is `1e-13 * sqrt(N)` per element (Option G).

---

## §7. Done criteria

- [ ] `backends/pascal/src/dft_kernel.pas` ships `Dft` + `Idft` + complex helpers with equation-to-code interface comment
- [ ] 4 test programs green: `make -C backends/pascal test` reports 5+6+14+(6 golden vectors × ~125 element-checks each) all PASS
- [ ] Worst-error numbers per test match Fortran reference within `2.22e-16` (or document the per-target FPC `Cos`/`Sin` 1-ULP delta in `STATUS-REPORT-FILLED.md`)
- [ ] `backends/pascal/Makefile` shim works (`make -C backends/pascal test` is the canonical invocation)
- [ ] Zero forbidden libraries (`grep -E "(uses.*pascalfft|uses.*ucomplex)" backends/pascal/src/*.pas backends/pascal/tests/*.pas` returns nothing)
- [ ] ASCII-only source files (`file backends/pascal/src/*.pas backends/pascal/tests/*.pas` reports ASCII text)
- [ ] Pre-flight sanitization grep clean per MASTER-BRIEF §5
- [ ] Tag at green: `git tag v0.0.6-pascal-port-green` after `make test` is all-green
- [ ] Commit message sequence per MASTER-BRIEF §3 §"Commit cadence"

---

## §8. If a gate fails

Walk this decision tree (identical to Rust except for Pascal-specific failure modes):

1. **Unit U1 (DC input) fails** — basic loop is wrong. Re-read `shared/canonical-equations/dft.md`. Ensure `acc.re := 0.0; acc.im := 0.0;` initialization (not just `acc := zero;` which Pascal handles fine but verify).

2. **U3 (complex unit at bin k) fails** — likely `ComplexMul` parenthesization. See §3 for the correct evaluation order.

3. **P8 fails at 1e-13 but passes at 9.1e-13** — expected. Set the gate constant to `9.1e-13` for P8.

4. **PT-DFT-03B fails at 1e-13 but passes at 1e-10** — expected. Set the gate to `1e-10` for PT-DFT-03B.

5. **Golden vectors fail at 1e-13 but pass at `1e-13 * sqrt(N)`** — Option G. Set the per-element gate to `1.0e-13 * Sqrt(Double(N))`.

6. **All tests pass individually but cross-language verify shows worst-error numbers differ from Fortran/C++ by more than `2.22e-16`** — most likely FPC `Cos`/`Sin` 1-ULP delta on your build target. Document in `STATUS-REPORT-FILLED.md` §"Cross-language verify". Pete will decide whether to absorb or weaken the Pascal gate by one ULP.

7. **Range-check error at runtime** — `-CR` flag caught an out-of-bounds array index. Find the off-by-one. Pascal arrays declared `array [0..N-1]` vs `array [1..N]` semantics differ from C/Rust 0-based — verify your loop bounds.

8. **Anything weirder** — park in `STATUS-REPORT-FILLED.md` §"Open blockers" with: what test, what value vs. expected, your hypothesis. Don't grind. Pete will look at it.

End of JOB-2-FOURIER-V0.2-PASCAL.md
