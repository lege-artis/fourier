package khsim

import io.circe.{Decoder, Encoder}
import io.circe.generic.semiauto.*

// ── Request ───────────────────────────────────────────────────────────────────

final case class SimulationRequest(
  gridNx:               Option[Int]    = None,
  gridNy:               Option[Int]    = None,
  domainLx:             Option[Double] = None,
  domainLy:             Option[Double] = None,
  dt:                   Option[Double] = None,
  steps:                Option[Int]    = None,
  reynoldsNumber:       Option[Double] = None,
  velocityShear:        Option[Double] = None,
  perturbationAmplitude:Option[Double] = None,
  perturbationMode:     Option[Int]    = None,
  initialOmega:         Option[Vector[Double]] = None,
):
  // Resolved values (openapi defaults)
  def nx:    Int    = gridNx.getOrElse(128)
  def ny:    Int    = gridNy.getOrElse(64)
  def lx:    Double = domainLx.getOrElse(1.0)
  def ly:    Double = domainLy.getOrElse(0.5)
  def dtVal: Double = dt.getOrElse(0.001)
  def nSteps:Int    = steps.getOrElse(100)
  def re:    Double = reynoldsNumber.getOrElse(1000.0)
  def u0:    Double = velocityShear.getOrElse(1.0)
  def amp:   Double = perturbationAmplitude.getOrElse(0.01)
  def mode:  Int    = perturbationMode.getOrElse(2)

// Circe snake_case codec (matches openapi.yaml field names)
object SimulationRequest:
  given Decoder[SimulationRequest] = Decoder.forProduct10(
    "grid_nx", "grid_ny", "domain_lx", "domain_ly", "dt", "steps",
    "reynolds_number", "velocity_shear", "perturbation_amplitude",
    "perturbation_mode",
  )((nx, ny, lx, ly, dt, steps, re, u0, amp, mode) =>
    SimulationRequest(nx, ny, lx, ly, dt, steps, re, u0, amp, mode))

// ── Response ──────────────────────────────────────────────────────────────────

final case class Diagnostics(
  kineticEnergy:  Double,
  enstrophy:      Double,
  maxVorticity:   Double,
  divergenceRms:  Double,
)
object Diagnostics:
  given Encoder[Diagnostics] = Encoder.forProduct4(
    "kinetic_energy", "enstrophy", "max_vorticity", "divergence_rms")(d =>
    (d.kineticEnergy, d.enstrophy, d.maxVorticity, d.divergenceRms))

final case class SimulationResult(
  backend:        String,
  language:       String,
  stepsCompleted: Int,
  tFinal:         Double,
  gridNx:         Int,
  gridNy:         Int,
  uVelocity:      Vector[Double],
  vVelocity:      Vector[Double],
  vorticity:      Vector[Double],
  pressure:       Vector[Double],
  diagnostics:    Diagnostics,
  computeTimeMs:  Double,
)
object SimulationResult:
  given Encoder[SimulationResult] = Encoder.forProduct12(
    "backend", "language", "steps_completed", "t_final",
    "grid_nx", "grid_ny",
    "u_velocity", "v_velocity", "vorticity", "pressure",
    "diagnostics", "compute_time_ms")(r =>
    (r.backend, r.language, r.stepsCompleted, r.tFinal,
     r.gridNx, r.gridNy,
     r.uVelocity, r.vVelocity, r.vorticity, r.pressure,
     r.diagnostics, r.computeTimeMs))

// ── Health / Info ─────────────────────────────────────────────────────────────

final case class HealthResponse(status: String, backend: String, port: Int)
object HealthResponse:
  given Encoder[HealthResponse] = deriveEncoder

final case class InfoResponse(
  backend:    String,
  language:   String,
  framework:  String,
  fftLibrary: String,
  port:       Int,
  openapiSpec:String,
)
object InfoResponse:
  given Encoder[InfoResponse] = Encoder.forProduct6(
    "backend", "language", "framework", "fft_library", "port", "openapi_spec")(r =>
    (r.backend, r.language, r.framework, r.fftLibrary, r.port, r.openapiSpec))
