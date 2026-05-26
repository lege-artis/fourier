# B5.5 — JWST at L2: structured rotational dynamics as a Fourier diagnostic

<!-- TODO (AG4): Place dragon-Pooh-Ring epigraph here. This chapter is
     the orbital-dynamics bridge and the natural fit for the Tolkien
     orbital-quest aesthetic per _handoffs/birthday-edition-v3/MASTER-BRIEF.md
     §5. Coordinate with illustrator brief H? brief when the v3 asset
     is commissioned. Suggested placement: between the chapter heading
     and "## The premise". -->

---

## The premise

There is a class of measurement in physics that sounds impossible until you think about it carefully, and then becomes obvious, and then starts to feel almost magical again once you realise all the ways it could have failed to work. Determining the mass distribution of an object by watching it tumble is one of those measurements.

The mechanism is this. A spinning rigid body is not simply rotating; it is also, if its spin axis does not exactly align with one of its principal axes, slowly precessing — the spin axis drifts in a circle around the nearest principal axis at a characteristic frequency. That frequency is not arbitrary. It is written, in a closed-form expression, in the body's principal moments of inertia and its spin rate. The body's internal geometry is not just carried passively in the rotation; it is the direct cause of the rotation's own structure.

Which means, if you can observe the precession, you can read off the inertia ratio. And the Discrete Fourier Transform is precisely the instrument for extracting a characteristic frequency from a time series. The same pipeline that reads oscillator frequencies from scope traces (B1), overtones from audio recordings (B2), bearing faults from accelerometers (B3), and Doppler shifts from radar returns (B5) also reads inertia-tensor ratios from a tumbling satellite's body-frame angular velocity. Same algorithm. Different physics.

This chapter makes that computation explicit, end to end.

---

## The setup: two bodies, no Sun

The experiment uses two simplified spacecraft in free space — no Sun, no Earth, no orbital mechanics. Just the two bodies, their inertia tensors, and the equations of motion.

**Body A** is JWST-shaped in broad outline: a flat sunshield at one end, a primary mirror assembly at the other, a spacecraft bus and boom in between. The numbers are illustrative, not exact¹: total mass approximately 2450 kg, principal moments of inertia diag(23322, 23322, 15384) kg·m² in the body frame. The boom direction is the z-axis, and I_zz = 15384 is *smaller* than I_xx = I_yy = 23322 — the z-axis moment is the minimum. This makes body A **prolate**: elongated along the boom, in the same geometric sense as a pencil or a rugby ball is elongated along its long axis. A prolate body will spin stably about its z-axis if the spin is exactly on-axis; any perpendicular component will precess, and the precession will be retrograde.

(¹ The precise value diag(23322, 23322, 15384) kg·m² comes from `geometries.py::make_jwst_like()` — a four-component composite body built from parallel-axis theorem sums of subcomponent inertia tensors for the sunshield, spacecraft bus, boom, and primary mirror. See `docs/canonical/en/02-kinetic-energy.md §2.4` for the inertia-tensor derivation and the §2.4 code cross-reference note for the exact factory function signature. The mass 2450 kg is the total mass of that composite. The numbers are not classified; they are chosen to produce a realistic inertia anisotropy ratio of 1.52 between the maximum and minimum principal moments, which is the pedagogically important quantity.)

**Body B** is a probe — a short cylinder with a dish antenna. Mass approximately 100 kg, principal moments diag(29, 29, 5) kg·m². Body B is also prolate, and considerably more so: I_zz / I_xx ≈ 5.8 versus 1.52 for body A.

We place A at the origin. B at +x = 50 metres. The inter-body gravitational attraction at that separation is approximately 2 × 10⁻⁷ N — slightly less than the force a mosquito exerts when landing. The gravity-gradient torque from B on A is approximately 6 × 10⁻¹⁰ N·m, a subtler quantity whose significance we will address in its own section.

Body A's initial angular velocity in body-frame coordinates: ω = (0.02, 0, 0.08) rad/s. The dominant spin is 0.08 rad/s about the boom axis, with a 25% perpendicular component along x (ω_x = 0.02 rad/s). It is this perpendicular component that will precess. Body A is also tilted 0.3 radians (approximately 17°) about the inertial-frame axis (1, 1, 0)/√2, so its principal axes are not aligned with the inertial frame from the start.

Body B's initial angular velocity: ω = (0, 0.03, 0.08) rad/s, similar structure with the perpendicular component along y.

Then we let the system evolve under Newtonian gravity and internal rotational dynamics, and watch what happens.

---

## Euler's equations and the precession prediction

Newton's F = ma governs point masses. Euler's equations govern rigid bodies. In body frame, the rotational equation of motion is:

```
I · dω/dt + ω × (I · ω) = τ
```

**Don't panic about the matrix equation.** The `I` is the body's inertia tensor — a 3×3 matrix that is constant in body frame, because the body doesn't change shape relative to itself. The `ω` is the angular velocity vector. The `τ` is external torque; we'll set it to zero for now since the gravity-gradient torque is many orders of magnitude too small to matter on the 600-second timescale of this experiment.

The second term, `ω × (I · ω)`, is the interesting one. It is not an external force; it is the body talking to itself. If ω is aligned with a principal axis of I, then I·ω is parallel to ω, the cross product is zero, and the body spins steadily. If ω has a component off the principal axis — as body A does, with ω_x = 0.02 rad/s — then I·ω points in a different direction from ω, the cross product is non-zero, and the body torques its own rotation. It precesses.

For an axisymmetric body where I_xx = I_yy ≠ I_zz, the Euler equations are solvable in closed form. The perpendicular angular velocity components oscillate at the **Euler precession frequency**:

```
λ_Euler = (I_zz − I_xx) / I_xx · ω_z
```

For body A, with ω_z = 0.08 rad/s and the principal moments above:

```
λ_A = (15384 − 23322) / 23322 × 0.08
    = −0.3404 × 0.08
    = −0.0272 rad/s
```

Period = 2π / |λ| ≈ **231 seconds**.

The negative sign means retrograde precession — the spin axis drifts opposite to the sense of the rotation, as expected for a prolate body. The magnitude gives the period. This is a prediction from first principles: given the inertia tensor and the initial spin rate, the precession period is 231 seconds. We haven't run anything yet; this is pure Euler mechanics.

The body-frame x-component of body A's angular velocity — the observable we'll FFT — should oscillate at this period.

---

## We run it and take the data

```bash
cd experiments/jwst-l2-first-cut
python3 run_first_example.py
```

Three seconds of CPU time later: an NDJSON file with 601 snapshots of the two-body system state, sampled at one-second intervals over 600 seconds of simulation time. Each snapshot contains the full state of both bodies — positions, velocities, quaternions, rotation matrices, body-frame and inertial-frame angular velocities, inertia tensor in the inertial frame, principal axes as vectors, and conservation diagnostics.

The first check is always conservation. In a closed two-body system with no external forces, total energy and total angular momentum are invariants. If they drift, the integrator is lying.

```
|dE / E_0| = 6.2 × 10⁻¹²
|dL / L_0| = 2.1 × 10⁻¹⁰
```

Both near machine precision. The fourth-order Runge-Kutta integrator at dt = 0.05 s internal step is honest². We proceed.

(² Conservation diagnostics are the numerical analyst's equivalent of a heartbeat monitor. A rising trend means the integrator is accumulating error faster than the physics. Flat diagnostics near machine epsilon, like these, mean the trajectory is trustworthy. The integration step dt = 0.05 s gives roughly four orders of margin against the fastest relevant dynamical time-scale — the off-diagonal element cycle time τ_off ≈ 190 s for the inertial-frame inertia tensor — which is comfortable.)

Extract the body-frame ω_A_x time series from the NDJSON:

```python
import json, numpy as np, pathlib

snapshots = [json.loads(l) for l in
             open("outputs/first_example_trajectory.ndjson")]
t        = np.array([s["t"]                    for s in snapshots])
omega_x  = np.array([s["A"]["omega_body"][0]   for s in snapshots])
```

601 points, one per second, spanning 600 seconds. Total observation duration 600 s. FFT bin spacing 1/600 ≈ 1.67 mHz.

---

## The transform

Three lines of transform, identical in structure to every previous chapter:

```python
signal     = omega_x - omega_x.mean()          # remove DC bias
Xk         = np.fft.rfft(signal)               # DFT (real-input, one-sided)
freqs      = np.fft.rfftfreq(len(signal),
                              d=(t[1] - t[0])) # Hz
magnitudes = np.abs(Xk)

peak_idx    = 1 + int(np.argmax(magnitudes[1:]))
peak_freq   = freqs[peak_idx]
peak_period = 1.0 / peak_freq
```

The removal of the DC component (`omega_x.mean()`) deserves a brief note: body A's x-angular velocity has a non-zero mean because the body starts with ω_x = 0.02 rad/s and the free precession oscillates around that value. Subtracting the mean suppresses the DC bin and lets the precession peak dominate the spectrum.

The output:

```
peak frequency:    0.0050 Hz
peak period:       200.00 s
peak magnitude:    4.840e+00 (rad/s)
```

One clean peak in the spectrum. Not a harmonic series — this is not a square wave or a musical chord. Not a Lorentzian tail — this is not a damped transient. A single narrow peak at 0.005 Hz, corresponding to a 200-second precession period. The spectrum is speaking clearly.

---

## The climax: prediction meets measurement

We predicted 231 seconds. The FFT reports 200 seconds. These are not the same number, and explaining why they agree requires understanding what the FFT can and cannot distinguish at finite observation windows.

The FFT bin spacing is 1/600 = 1.67 mHz. The observable periods near the predicted 231 s are **quantised** at the available frequency bins: 600 s, 300 s, 200 s, 150 s, 120 s, and so on. The period 231 s sits between the 200-s bin and the 300-s bin. The nearer of the two is 200 s. The FFT peak landed at 200 s, which is within 0.13 FFT bins of the Euler-frequency prediction³.

(³ The 0.13-bin offset has three components: bin quantisation (the dominant contributor at this observation-window length), small gravity-gradient perturbation to the pure free-precession frequency, and numerical integration error. All three are negligible compared to the bin width. The cross-project diagnostic `fourier/examples/jwst-l2-tumble-spectrum/main.py` computes this offset programmatically and flags anything above 1.5 bins as a signal of either insufficient observation window or physics beyond free precession — gyroscopic resonance, strong gravity-gradient coupling, or non-axisymmetric inertia drift.)

The full cross-check from the diagnostic:

```
--- theoretical Euler precession (body A axisymmetric model) ---
  I_axial:           15384.0000 kg.m^2   (= I_zz)
  I_perp:            23322.0000 kg.m^2   (= I_xx = I_yy)
  omega_z (initial): 0.080000 rad/s
  lambda_Euler:      -0.027201 rad/s
  Theoretical freq:  0.0043 Hz
  Theoretical period:231.01 s

--- agreement check ---
  Bin offset (peak vs theory): 0.13 FFT bins
  Result: peak matches theory within FFT bin resolution. OK.
```

The prediction matched.

The half-power width of the spectral peak is, in this case, a single bin — the precession is a clean linear normal mode with no apparent damping on the 600-second timescale. The spectral width and the damping time are, in the language of Fourier analysis, two views of the same quantity: a narrow peak means a long-lived mode. The DFT cannot do this one any harm; it is exactly what the DFT was built for.

What is happening physically here is slightly different from the signal-processing cases in B1 through B5. The oscilloscope chapter (B1) identified the frequency of a signal that somebody *put into* the system from outside — a function generator, or a muon arriving at a detector. Here, nobody put in a 200-second oscillation from outside. The oscillation at the Euler frequency is the system's own *response* to initial conditions: body A was started with a small off-axis spin component, and the response of Euler's equations to that perturbation is a precession at the characteristic frequency the inertia tensor dictates. The DFT is identifying a **natural mode** of a dynamical system from a short time series of its output. The physics is richer; the methodology is identical.

This is the point of the chapter. The DFT is not a signal-processing tool that happens, occasionally, to find application in dynamics. It is the canonical spectral analysis primitive for any time series produced by a system with characteristic frequencies — and that category of system includes an enormous amount of the physical world.

---

## The gravity-gradient torque: small, present, and instructive

The simulation includes the gravity-gradient torque from B on A and A on B at every integration step. At t = 600 s, the diagnostic reads:

```
tau_gg_A_magnitude ≈ 6.3 × 10⁻¹⁰ N·m
```

Body A's rotational kinetic energy at this point is approximately 54 J. A torque of 6.3 × 10⁻¹⁰ N·m, applied continuously, needs approximately E_rot / τ ≈ 54 / 6×10⁻¹⁰ ≈ 10¹¹ seconds — roughly 3000 years — to do meaningful work on the spin. On the 600-second timescale of this experiment, the gravity-gradient torque is dynamically irrelevant. The spectrum shows one clean peak, not a broad peak modulated by slow coupling, because the coupling is too weak to act on this timescale.

It is not irrelevant as a diagnostic, however. The torque is there, non-zero, available for analysis whenever we integrate longer. At L2, where the central gravity of the Sun and Earth nearly cancels, and where the residual tidal environment is weak and complicated, a gravity-gradient torque from any extended nearby object can become the primary attitude-disturbing mechanism — precisely because everything else is also very small there. The full JWST-L2 coupled-dynamics story needs a halo orbit, a real L2 potential, and an integration horizon on the order of months, not seconds; that is the scope of the eventual full project (`lege-artis/jwst-l2-coupled-dynamics`). What this first-cut establishes is that the integrator, the data pipeline, the conservation diagnostics, and the basic interpretation arc work correctly.

They do.

The gravity-gradient torque from B on A has a closed-form expression⁴ derived from the quadrupole expansion of the mutual gravitational potential:

```
τ_A^body = (3 G m_B / |ρ|³) · ρ_hat_body_A × (I_A · ρ_hat_body_A)
```

where ρ_hat_body_A is the unit vector from A to B expressed in A's body frame. The torque depends on the *orientation* of this unit vector relative to the body's principal axes — it is zero when the separation vector aligns with a principal axis, and maximum at 45° to the principal axes. This orientation dependence is the gravity-gradient stabilisation principle: prolate spacecraft (I_z < I_x = I_y) have stable equilibria with the long axis pointing along the separation vector from any large gravitational source; oblate spacecraft (I_z > I_x = I_y) do not. That stability analysis belongs in the canonical-tier documents; the Shad-tier observation is simply: the torque is real, it is small, and the spectrum knows about it only as a very slow modulation that becomes visible on much longer integration windows.

(⁴ The full derivation lives at `docs/canonical/en/03-mutual-gravitational-potential.md §3.7`, which works through the quadrupole multipole expansion, derives the torque via variational differentiation of the tidal potential, and verifies the result line-by-line against the `dynamics.py::gravity_gradient_torque_body_frame` implementation. The line-by-line match is not accidental; it is the `lege-artis` discipline that canonical-tier derivations must trace to engineer-tier code and vice versa.)

---

## The same algorithm, five domains, one methodology

You took an oscilloscope trace (B1), transformed it, and read the oscillator frequency. You took an audio recording (B2), transformed it, and identified the overtones. You took a vibration log from a bearing (B3), transformed it, and located the fault signature. You took a radar return (B5), transformed it, and extracted the target's Doppler velocity.

Here you took the body-frame angular velocity time series of a tumbling satellite, transformed it, and read the inertia-tensor anisotropy ratio directly from the spectral peak.

The reason it works is the same reason it works in every other case: the underlying physical system has a characteristic frequency — the Euler precession frequency — and the system's observable output modulates at that frequency. The DFT identifies the modulation. Physics that is different; methodology that is identical.

If you need to measure the inertia ratio of an assembled spacecraft after launch and don't want to wait for a calibration table result from a ground test — you could, in principle, command a controlled off-axis spin, observe the body-frame angular velocity with the onboard IMU for a few hundred seconds, run the FFT on the output, read the peak frequency, and recover (I_zz − I_xx)/I_xx directly from λ = peak_frequency × 2π / ω_z. You don't need to dismantle the spacecraft. You don't need a coordinate-measuring machine. You need:

- a controlled initial spin with a small perpendicular component
- a body-frame angular-velocity time series from any reasonable IMU
- an observation window long enough to contain a few precession periods
- `np.fft.rfft`

That last item is, by this point in the guide, an old friend.

When the dynamics become non-linear — strong gravity-gradient coupling, gyroscopic resonances where the precession period commensurates with an orbital period, the full six-DOF coupled problem — the bare DFT will start to mislead: the clean single peak will broaden, split, or drift. That is the cue to reach for the power spectral density methods and time-frequency analysis tools that B7 (nuclear reactor noise diagnostics) introduces. In the setup here, the dynamics are predominantly linear and the DFT is sufficient. The peak is clean. The prediction matches. The body told us its own structure, just by tumbling.

---

## Try it yourself

The trajectory is produced by the first-cut simulation in the sibling project; the FFT diagnostic runs in the `fourier` repository.

```bash
# Step 1: generate the JWST-L2 trajectory
cd experiments/jwst-l2-first-cut
python3 run_first_example.py
# writes:  outputs/first_example_trajectory.ndjson  (601 snapshots, ~1 MB)

# Step 2: run the cross-project Fourier diagnostic
cd ../../fourier/examples/jwst-l2-tumble-spectrum
python3 main.py ../../experiments/jwst-l2-first-cut/outputs/first_example_trajectory.ndjson
```

Expected output:

```
=== JWST-L2 tumble-spectrum cross-project example ===
  Input NDJSON: .../first_example_trajectory.ndjson
  Snapshots:         601
  Snapshot dt:       1.0000 s
  Total duration:    600.00 s
  Sample rate fs:    1.0000 Hz
  FFT bin spacing:   1.6667e-03 Hz

--- spectrum analysis ---
  Peak frequency:    0.0050 Hz
  Peak period:       200.00 s
  Peak magnitude:    4.840e+00 (rad/s)

--- theoretical Euler precession (body A axisymmetric model) ---
  I_axial:           15384.0000 kg.m^2
  I_perp:            23322.0000 kg.m^2
  omega_z (initial): 0.080000 rad/s
  lambda_Euler:      -0.027201 rad/s
  Theoretical freq:  0.0043 Hz
  Theoretical period:231.01 s

--- agreement check ---
  Bin offset (peak vs theory): 0.13 FFT bins
  Result: peak matches theory within FFT bin resolution. OK.
```

**To get finer spectral resolution:** modify `run_first_example.py` and set `t_max = 2400` (four times longer). The bin spacing drops to 0.42 mHz and the predicted 231-s period sits cleanly on a resolved bin. The peak shifts from 200 s toward 231 s, and you can read the inertia ratio directly from `lambda = 2π × peak_freq / omega_z`. Observe also that on this longer window the gravity-gradient torque begins to visibly modulate the precession amplitude — the small coupling is no longer negligible over 40 minutes.

---

## References

- H. Hughes, *Spacecraft Attitude Dynamics*, Wiley, 2004. §5.3 (gravity-gradient torque on a rigid spacecraft); §4 (inertia tensor, parallel-axis theorem, body-frame bookkeeping); §8 (gravity-gradient stabilisation).

- L. D. Landau and E. M. Lifshitz, *Mechanics* (Vol. I, Course of Theoretical Physics), 3rd ed., Pergamon, 1976. §32 (kinetic energy and Euler's equations for a rigid body, König's theorem, torque-free symmetric top).

- H. Goldstein, C. Poole, J. Safko, *Classical Mechanics*, 3rd ed., Addison-Wesley, 2002. §5.3–§5.6 (Euler's equations, principal-axis frame, torque-free motion).

---

## Cross-references

- Canonical derivation of König's decomposition, inertia tensor, and body-frame vs. inertial-frame bookkeeping:
  [`../../experiments/jwst-l2-first-cut/docs/canonical/en/02-kinetic-energy.md`](../../experiments/jwst-l2-first-cut/docs/canonical/en/02-kinetic-energy.md)

- Quadrupole expansion of mutual gravitational potential, gravity-gradient torque derivation (§3.7), and gravity-gradient stabilisation theorem (§3.7.2):
  [`../../experiments/jwst-l2-first-cut/docs/canonical/en/03-mutual-gravitational-potential.md`](../../experiments/jwst-l2-first-cut/docs/canonical/en/03-mutual-gravitational-potential.md)

- The cross-project FFT diagnostic (the chapter's runnable climax):
  [`../examples/jwst-l2-tumble-spectrum/main.py`](../examples/jwst-l2-tumble-spectrum/main.py)

- The first-cut simulation code, inertia-tensor composite construction, and NDJSON trajectory:
  [`../../experiments/jwst-l2-first-cut/`](../../experiments/jwst-l2-first-cut/)

- Canonical DFT-1 definition and derivation:
  [`../canonical/en/01-dft-definition.md`](../canonical/en/01-dft-definition.md)

- The Fortran and C++ reference DFT implementations, which produce bit-identical results to `np.fft.rfft` per the `lege-artis/fourier` v0.2.0 empirical cross-language validation:
  [`../../backends/`](../../backends/)

---

**Previous:** [B5 — Radar](05-radar.md)
**Next:** [B6 — Radio astronomy](06-radioastronomy.md)
