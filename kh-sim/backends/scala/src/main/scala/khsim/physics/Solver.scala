package khsim.physics

import khsim.{Diagnostics, SimulationRequest, SimulationResult}

/** KH instability physics kernel — Scala port of kh_physics.py.
  *
  * Physics: 2D incompressible Navier-Stokes, vorticity-streamfunction form.
  * Numerics: pseudo-spectral (JTransforms 2D FFT) + RK4 time integration.
  *
  * Reference: kh-sim/shared/physics/KH-PHYSICS.md
  * Canonical: kh-sim/shared/physics/kh_physics.py
  */
object Solver:

  // ── Initial conditions ─────────────────────────────────────────────────────

  private def initialConditions(
    nx: Int, ny: Int, lx: Double, ly: Double,
    u0: Double, delta: Double, amp: Double, mode: Int,
  ): Array[Double] =
    val dx    = lx / nx
    val dy    = ly / ny
    val omega = new Array[Double](nx * ny)
    var i = 0
    while i < nx do
      val x = i * dx
      val pertX = amp * (2.0 * math.Pi * mode / lx) * math.cos(2.0 * math.Pi * mode * x / lx)
      var j = 0
      while j < ny do
        val y     = j * dy
        val z     = (y - ly / 2.0) / delta
        val shear = u0 / delta / (math.cosh(z) * math.cosh(z))
        omega(i * ny + j) = shear + pertX
        j += 1
      i += 1
    omega

  // ── Spectral Poisson solve ─────────────────────────────────────────────────

  /** psi_hat = omega_hat / k^2 ; psi_hat[0] = 0 (zero mean). */
  private def solvePoisson(
    omegaHat: Array[Double],  // interleaved complex, length 2*nx*ny
    kx: Array[Double],
    ky: Array[Double],
    nx: Int, ny: Int,
  ): Array[Double] =
    val psiHat = omegaHat.clone()
    var i = 0
    while i < nx do
      var j = 0
      while j < ny do
        val idx = i * ny + j
        val k2  = kx(idx) * kx(idx) + ky(idx) * ky(idx)
        if i == 0 && j == 0 then
          psiHat(0) = 0.0
          psiHat(1) = 0.0
        else
          val re = omegaHat(2 * idx)
          val im = omegaHat(2 * idx + 1)
          psiHat(2 * idx)     = re / k2
          psiHat(2 * idx + 1) = im / k2
        j += 1
      i += 1
    psiHat

  // ── Velocity from streamfunction ───────────────────────────────────────────

  /** u_hat = i*ky*psi_hat,  v_hat = -i*kx*psi_hat */
  private def velocityFromPsiHat(
    psiHat: Array[Double],
    kx: Array[Double],
    ky: Array[Double],
    fft: Fft2D,
  ): (Array[Double], Array[Double]) =
    val n     = fft.nx * fft.ny
    val uHat  = new Array[Double](2 * n)
    val vHat  = new Array[Double](2 * n)
    var k = 0
    while k < n do
      val re = psiHat(2 * k)
      val im = psiHat(2 * k + 1)
      // i * ky * (re + i*im) = ky*(-im) + i*ky*re
      uHat(2 * k)     = -ky(k) * im
      uHat(2 * k + 1) =  ky(k) * re
      // -i * kx * (re + i*im) = kx*im + i*(-kx*re)
      vHat(2 * k)     =  kx(k) * im
      vHat(2 * k + 1) = -kx(k) * re
      k += 1
    (fft.ifft2Real(uHat), fft.ifft2Real(vHat))

  // ── Vorticity RHS ──────────────────────────────────────────────────────────

  private def vorticityRhs(
    omega: Array[Double],
    u: Array[Double],
    v: Array[Double],
    nu: Double,
    kx: Array[Double],
    ky: Array[Double],
    fft: Fft2D,
  ): Array[Double] =
    val n        = fft.nx * fft.ny
    val omegaHat = fft.fft2(omega)

    // spectral gradients: domega/dx, domega/dy
    val dxSpec = new Array[Double](2 * n)
    val dySpec = new Array[Double](2 * n)
    val lapSpec = new Array[Double](2 * n)
    var k = 0
    while k < n do
      val re = omegaHat(2 * k)
      val im = omegaHat(2 * k + 1)
      // i*kx*(re+i*im) = -kx*im + i*kx*re
      dxSpec(2 * k)     = -kx(k) * im
      dxSpec(2 * k + 1) =  kx(k) * re
      // i*ky*(re+i*im)
      dySpec(2 * k)     = -ky(k) * im
      dySpec(2 * k + 1) =  ky(k) * re
      // -(kx^2+ky^2) * (re+i*im)
      val k2 = kx(k) * kx(k) + ky(k) * ky(k)
      lapSpec(2 * k)     = -k2 * re
      lapSpec(2 * k + 1) = -k2 * im
      k += 1

    val dOmegaDx = fft.ifft2Real(dxSpec)
    val dOmegaDy = fft.ifft2Real(dySpec)
    val lapOmega = fft.ifft2Real(lapSpec)

    val rhs = new Array[Double](n)
    var i = 0
    while i < n do
      rhs(i) = -u(i) * dOmegaDx(i) - v(i) * dOmegaDy(i) + nu * lapOmega(i)
      i += 1
    rhs

  // ── Helpers ────────────────────────────────────────────────────────────────

  private def addScaled(a: Array[Double], b: Array[Double], s: Double): Array[Double] =
    val out = new Array[Double](a.length)
    var i = 0
    while i < a.length do
      out(i) = a(i) + s * b(i)
      i += 1
    out

  // ── RK4 step ───────────────────────────────────────────────────────────────

  private def rk4Step(
    omega: Array[Double],
    nu: Double,
    kx: Array[Double],
    ky: Array[Double],
    fft: Fft2D,
    dt: Double,
  ): Array[Double] =
    def f(w: Array[Double]): Array[Double] =
      val wHat   = fft.fft2(w)
      val psiHat = solvePoisson(wHat, kx, ky, fft.nx, fft.ny)
      val (u, v) = velocityFromPsiHat(psiHat, kx, ky, fft)
      vorticityRhs(w, u, v, nu, kx, ky, fft)

    val k1 = f(omega)
    val k2 = f(addScaled(omega, k1, 0.5 * dt))
    val k3 = f(addScaled(omega, k2, 0.5 * dt))
    val k4 = f(addScaled(omega, k3, dt))

    val out = new Array[Double](omega.length)
    var i = 0
    while i < omega.length do
      out(i) = omega(i) + (dt / 6.0) * (k1(i) + 2*k2(i) + 2*k3(i) + k4(i))
      i += 1
    out

  // ── Diagnostics ────────────────────────────────────────────────────────────

  private def mean(a: Array[Double]): Double =
    var s = 0.0; var i = 0
    while i < a.length do { s += a(i); i += 1 }
    s / a.length

  private def meanSq(a: Array[Double]): Double =
    var s = 0.0; var i = 0
    while i < a.length do { s += a(i) * a(i); i += 1 }
    s / a.length

  private def maxAbs(a: Array[Double]): Double =
    var m = 0.0; var i = 0
    while i < a.length do { val v = math.abs(a(i)); if v > m then m = v; i += 1 }
    m

  private def computeDiagnostics(
    omega: Array[Double],
    u: Array[Double],
    v: Array[Double],
    kx: Array[Double],
    ky: Array[Double],
    fft: Fft2D,
  ): Diagnostics =
    val n   = fft.nx * fft.ny
    val ke  = 0.5 * mean(Array.tabulate(n)(i => u(i)*u(i) + v(i)*v(i)))
    val ens = 0.5 * meanSq(omega)
    val mv  = maxAbs(omega)

    // Divergence via spectral differentiation
    val uHat = fft.fft2(u)
    val vHat = fft.fft2(v)
    val divSpec = new Array[Double](2 * n)
    var k = 0
    while k < n do
      val dxRe = -kx(k) * uHat(2*k+1)
      val dxIm =  kx(k) * uHat(2*k)
      val dyRe = -ky(k) * vHat(2*k+1)
      val dyIm =  ky(k) * vHat(2*k)
      divSpec(2*k)   = dxRe + dyRe
      divSpec(2*k+1) = dxIm + dyIm
      k += 1
    val div    = fft.ifft2Real(divSpec)
    val divRms = math.sqrt(meanSq(div))

    Diagnostics(ke, ens, mv, divRms)

  // ── Main entry point ───────────────────────────────────────────────────────

  def simulate(req: SimulationRequest): SimulationResult =
    val t0     = System.nanoTime()
    val nx     = req.nx
    val ny     = req.ny
    val lx     = req.lx
    val ly     = req.ly
    val dt     = req.dtVal
    val nSteps = req.nSteps
    val nu     = req.u0 / req.re
    val delta  = 0.05 * ly

    val dx = lx / nx
    val dy = ly / ny

    val fft         = new Fft2D(nx, ny)
    val (kx, ky)    = Wavenumbers.make(nx, ny, dx, dy)

    var omega: Array[Double] = req.initialOmega match
      case Some(v) =>
        require(v.length == nx * ny, "initialOmega length must equal nx*ny")
        v.toArray
      case None =>
        initialConditions(nx, ny, lx, ly, req.u0, delta, req.amp, req.mode)

    var t = 0.0
    var step = 0
    while step < nSteps do
      omega  = rk4Step(omega, nu, kx, ky, fft, dt)
      t     += dt
      step  += 1

    // Final field recovery
    val omegaHat    = fft.fft2(omega)
    val psiHat      = solvePoisson(omegaHat, kx, ky, nx, ny)
    val psi         = fft.ifft2Real(psiHat)
    val (u, v)      = velocityFromPsiHat(psiHat, kx, ky, fft)
    val diagnostics = computeDiagnostics(omega, u, v, kx, ky, fft)

    val elapsedMs = (System.nanoTime() - t0) / 1e6
    val tRounded  = math.round(t * 1e10) / 1e10

    SimulationResult(
      backend        = "scala-http4s",
      language       = "Scala",
      stepsCompleted = nSteps,
      tFinal         = tRounded,
      gridNx         = nx,
      gridNy         = ny,
      uVelocity      = u.toVector,
      vVelocity      = v.toVector,
      vorticity      = omega.toVector,
      pressure       = psi.toVector,
      diagnostics    = diagnostics,
      computeTimeMs  = math.round(elapsedMs * 100) / 100.0,
    )
