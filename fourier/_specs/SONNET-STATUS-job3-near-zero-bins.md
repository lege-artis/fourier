# Sonnet Status — Job-3 follow-up — near-zero-bin gate failures after hybrid abs-rel fix

**Job:** Job-3 (Golden-vector loader + verification) — second escalation
**Status:** STOP per handoff §7 + per Opus rule "if 43/43 doesn't go green after the gate change, escalate back to me". Hybrid fix closed 1 of 7 prior failures; 6 remain at near-zero output bins where the hybrid metric degenerates to absolute.
**Author:** Sonnet (MacBook Cowork session, 2026-05-09 PM)
**Locks-in version:** Local commit `4dafb38` on macbook branch (Pete committed before recognising the gate-run was still red — see §6); previous status doc `_specs/SONNET-STATUS-job3-precision-gate.md` already on disk.
**Reproduction host:** MacBook Intel + macOS Tahoe + gfortran-15 + /usr/bin/python3 (3.9.6) — same as prior STATUS

---

## §0. TL;DR for Opus

| Metric | Before hybrid fix | After hybrid fix |
|---|---|---|
| Unit tests | 5/5 PASS | 5/5 PASS |
| Golden tests | 31/38 PASS, 7 FAIL | **32/38 PASS, 6 FAIL** |
| Total | 36/43 | **37/43** |

Hybrid gate (`abs / max(|expected|, 1.0_dp) < 1e-13`) **closed exactly one failure**: `golden_n64_ramp idx 63` (was 9.855e-12 abs at |expected|≈1000 → now 9.855e-15 rel = PASS). Confirms the hybrid mechanism is sound for **large-magnitude** bins.

The 6 remaining failures are all **near-zero output bins** where `|expected| < 1e-10`. For these the hybrid `max(|expected|, 1.0_dp)` clamps the divisor to 1.0, so the metric reduces to absolute error — and absolute error at N=64 on near-zero bins hits ~1-3e-13 from cancellation of 64 summed terms.

---

## §1. The 6 remaining failures (all N=64; all near-zero bins)

| Failure | idx | max-rel-err | max-abs-err | |expected| | display (actual / expected) |
|---|---|---|---|---|---|
| `golden_n64_cosine_k1` | 61 | **1.071e-13** | 1.071e-13 | ~0 | `0.0 + 0.0i / -0.0 + -0.0i` |
| `golden_n64_cosine_k2` | 61 | **2.078e-13** | 2.078e-13 | ~0 | `0.0 + -0.0i / 0.0 + 0.0i` |
| `golden_n64_sine_k1` | 55 | **1.268e-13** | 1.268e-13 | ~0 | `-0.0 + -0.0i / 0.0 + 0.0i` |
| `golden_n64_cos1_plus_cos2` | 61 | **3.092e-13** | 3.092e-13 | ~0 | `0.0 + -0.0i / 0.0 + 0.0i` |
| `golden_n64_dc_one` | 63 | **1.618e-13** | 1.618e-13 | ~0 | `0.0 + -0.0i / 0.0 + 0.0i` |
| `golden_n64_ramp` | 29 | **1.529e-13** | **4.945e-12** | ~32 | `-32.0 + 4.74675160i / -32.0 + 4.74675160i` |

Note the last row (`ramp idx 29`): max-abs-err is 4.945e-12 but max-rel-err is 1.529e-13 — confirming the hybrid mechanism IS scaling for `|expected|` ≈ 32. It just doesn't scale enough — a relative gate of 1e-13 is right at machine precision (eps ≈ 2.22e-16) × sqrt(64) summation × ~1.5 round-off-multiplier ≈ 2.7e-15... hmm that's 50x below 1.5e-13. Something else is happening on this case — see §3.

---

## §2. Why the hybrid gate doesn't catch near-zero bins

The chosen metric:
```
metric = abs(actual - expected) / max(abs(expected), 1.0_dp)
```

When `|expected| < 1`: divisor = 1.0_dp → metric = absolute error.
When `|expected| > 1`: divisor = `|expected|` → metric = relative error.

The first 5 failures ALL have `|expected| ≪ 1` (essentially zero by mathematical construction — cosine/sine/DC at orthogonal frequency bins). The hybrid gate is therefore reduced to absolute error for these, with no scaling benefit.

Direct DFT round-off at N=64 on a bin that mathematically equals zero:
- 64 terms of the form `x[n] * cmplx(cos, sin)` are summed
- Each term has magnitude up to `|x|max` and contributes `eps * |x|max` round-off
- For pure cosine input with `|x|max = 1`: 64 * 2.22e-16 = 1.4e-14 worst-case
- But cancellation amplifies this — 64 numbers of similar magnitude that should cancel to zero accumulate the differences ~sqrt(64) * eps = 1.8e-15 in random-walk terms, but in CORRELATED-cancellation cases (cos at freq 1 evaluated at bin 61 ≈ -bin 3 with sign flip in the kernel) the round-off can reach ~1e-13.

This is a **known limitation of direct (unblocked) DFT summation**. FFT (numpy/pocketfft) gets cancellation right via the butterfly structure that cancels paired terms in O(log N) rather than O(N) accumulator updates.

**Diagnosis confidence: HIGH.** The 5 cases all match the pattern: large input magnitudes (`x = cos`, `x = sin`, `x = ramp`, `x = dc_one`) summed with phase factors at bin frequencies that should yield zero but yield ~1e-13.

---

## §3. The 6th case (ramp idx 29) is partially scaled — why not more?

`golden_n64_ramp idx 29`: `expected = -32.0 + 4.74675160i` (magnitude ~32), abs-err 4.945e-12, rel-err 1.529e-13.

Sanity: 4.945e-12 / 32.0 = 1.55e-13 — matches the reported rel-err exactly. So the hybrid mechanism IS scaling correctly. The metric just lands above 1e-13.

Why? The ramp DC bin at idx 0 is `sum(0..63) = 2016`. Round-off there could reach 64 × 2.22e-16 × 2016 = 2.9e-11. The other bins of the ramp DFT have magnitudes ~32 (the formula gives non-DC bins ≈ N / (2 * sin(pi*k/N))). Each non-DC bin is computed as `sum_{n} n * exp(-2*pi*i*k*n/N)` — a sum of 64 terms of magnitude up to 63 each. The accumulated round-off is 64 * 2.22e-16 * 63 = 9e-13 absolute, or 9e-13 / 32 = 2.8e-14 relative...

Hmm that suggests it should pass at 1e-13 relative. But it's failing at 1.5e-13 relative. So either:
- The accumulator's worst case isn't sqrt(N) × eps × max-term but something larger (cancellation in the inner sum)
- Or there's a specific numerical pathology at idx 29 (k=29, N=64 is near k=N/2 where the trigonometric values cluster)

In any case, this case is RIGHT AT the gate boundary (1.5e-13 vs 1e-13 → factor of 1.5 over). Either widen the gate slightly OR it joins the noise-floor cases.

---

## §4. Three remediations (Opus to choose)

In order of "simplest absolute" to "most architecturally right":

### §4.1 Option E — Widen the gate from 1e-13 to 1e-12

Smallest change. Single-line edit:
```fortran
real(dp), parameter :: tol = 1.0e-12_dp   ! was 1.0e-13_dp
```
Test ALL 6 remaining failures pass (max is 3.092e-13 — well below 1e-12).

**Pros:** trivial; preserves hybrid metric; all 38 cases pass cleanly.
**Cons:** the published "1e-13 gate" advertised in WORKING-SPEC and handoff §1.5 becomes "1e-12 gate" — a 10x relaxation. This may matter for downstream FFT validation when v0.2.0 lands; FFT rounds-off at ~1e-15 typically and would need a tighter gate.

### §4.2 Option F — Hybrid abs-rel WITH noise floor

Change the divisor from `max(|expected|, 1.0_dp)` to `max(|expected|, noise_floor_for_this_N)`:

```fortran
! noise_floor scales with N (cancellation accumulation worst-case)
noise_floor = real(nlen, dp) * 5.0e-15_dp   ! ~ N * (~22 * eps) for safety
rel_err = abs_err / max(abs(expected(i)), noise_floor)
```

For N=64: `noise_floor = 64 * 5e-15 = 3.2e-13`. The 6 cases would have:
- cosine_k1 idx 61: 1.071e-13 / 3.2e-13 = 0.33 → PASS
- cos1_plus_cos2 idx 61: 3.092e-13 / 3.2e-13 = 0.97 → PASS (just under)
- ramp idx 29: 4.945e-12 / 32 (because |expected|=32 > 3.2e-13) = 1.55e-13 — STILL FAILS

So Option F fixes the 5 near-zero cases but NOT the ramp idx 29 case. Need to combine with Option E (widen tol to 1e-12) for ramp.

**Pros:** more principled; properly accounts for cancellation noise floor; preserves "1e-13 typical" claim while permitting noise-floor escape.
**Cons:** introduces N-dependent floor (one more parameter to track); doesn't single-handedly fix ramp idx 29.

### §4.3 Option G — Hybrid abs-rel + N-scaled tolerance + magnitude floor

Combine: tolerance scales with N, and divisor is max(|expected|, 1.0). For each case, the gate is:
```
metric = abs(actual - expected) / max(abs(expected), 1.0_dp)
gate   = 1.0e-13_dp * sqrt(real(nlen, dp))
```

For N=64: gate = 1e-13 * 8 = 8e-13. All 6 cases pass.

**Pros:** mathematically grounded (sqrt(N) is the natural FP accumulator scaling per Higham §4.2); single principle covers all cases including the ramp idx 29.
**Cons:** the "1e-13 published contract" becomes "1e-13 * sqrt(N)" — needs documentation; large N would have generously wide gates.

---

## §5. MacBook recommendation

**Option G** (sqrt(N)-scaled tol + hybrid abs-rel) is the architecturally cleanest and matches the actual numerical analysis. **Option E** (just widen to 1e-12) is the simplest if you want to ship Job-3 today and revisit later when FFT lands. **Option F** is in between.

If you pick **G**, the helper code change is:
```fortran
subroutine assert_complex_array_close(test_name, actual, expected, tol_base)
    ...
    real(dp), intent(in) :: tol_base
    real(dp) :: tol
    ...
    tol = tol_base * sqrt(real(size(actual), dp))   ! N-scaled per Higham §4.2
    ...
    if (max_rel_err > tol) then
```

If you pick **E**, the helper signature is unchanged; just the tol literal in `test_one_n` changes from `1.0e-13_dp` to `1.0e-12_dp`.

---

## §6. About commit `4dafb38`

Pete ran `git commit` immediately after `make test` exited red. The commit message says "widen ... from absolute to hybrid abs-rel" but the actual gate-run shipped 32/38 (not 43/43 as the commit narrative implies). Three disposition options:

1. **`git commit --amend`** — once Opus picks a remediation from §4, apply, re-test, amend the existing commit (preserves a single clean commit).
2. **Follow-up commit** — keep `4dafb38` as-is; add a new commit "fix(test): close remaining 6 near-zero-bin failures via [Option E/F/G]" with the second iteration.
3. **`git reset HEAD~1`** — drop `4dafb38` entirely, redo as one commit after the fix lands.

I lean toward (1) amend — the v0.0.5 tag should be a single clean commit landing 43/43.

---

## §7. Status footer

| Item | Value |
|------|-------|
| Document | `_specs/SONNET-STATUS-job3-near-zero-bins.md` |
| Trigger | 32/38 PASS / 6 FAIL after applying Opus-authorised hybrid abs-rel gate (Option B from prior STATUS) |
| Failures pattern | 5 near-zero bins (|expected| < 1e-10) + 1 medium-magnitude (|expected|≈32) at N=64 only |
| Remaining errors | 1.071e-13 to 4.945e-12 (abs); 1.071e-13 to 3.092e-13 (rel via hybrid) |
| Diagnosis confidence | HIGH — round-off-at-cancellation-boundary on direct DFT at N=64 |
| Kernel touched | NO (per §1.6) |
| Specs touched | NO |
| Sonnet decision | STOP per Opus rule "if 43/43 doesn't go green, escalate back to me" |
| Status | escalated #2; awaiting Opus pick from §4 (E / F / G) + decision on commit `4dafb38` from §6 |

---

*SONNET-STATUS-job3-near-zero-bins.md — 2026-05-09 PM — MacBook Cowork session — Sonnet (post Claude 1.6259.1 update)*
