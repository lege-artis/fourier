package khsim

import io.circe.parser.*
import io.circe.{Decoder, HCursor}
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

import java.nio.file.{Files, Paths}

/** KH-004 acceptance test — validates Scala diagnostics against
  * kh-sim/shared/physics/kh_reference_output.json.
  *
  * Tolerance: +-5% on kinetic_energy and enstrophy (KH-PHYSICS.md S7).
  * Incompressibility: divergence_rms < 1e-10.
  *
  * Run: sbt test
  */
class ValidationTest extends AnyFunSuite with Matchers:

  // ── Load reference JSON ─────────────────────────────────────────────────────

  private case class RefDiag(
    kineticEnergy: Double,
    enstrophy:     Double,
    maxVorticity:  Double,
    divergenceRms: Double,
  )

  private given Decoder[RefDiag] = (c: HCursor) =>
    for
      ke  <- c.downField("kinetic_energy").as[Double]
      ens <- c.downField("enstrophy").as[Double]
      mv  <- c.downField("max_vorticity").as[Double]
      div <- c.downField("divergence_rms").as[Double]
    yield RefDiag(ke, ens, mv, div)

  private case class RefOutput(nx: Int, ny: Int, steps: Int, diag: RefDiag)

  private def loadReference(): RefOutput =
    // Path relative to sbt project root (kh-sim/backends/scala/)
    val path = Paths.get("../../shared/physics/kh_reference_output.json")
    assert(
      Files.exists(path),
      s"Reference file not found: $path -- run python kh_physics.py first"
    )
    val raw  = new String(Files.readAllBytes(path))
    val json = parse(raw).getOrElse(throw new RuntimeException("Bad JSON"))
    val c    = json.hcursor
    RefOutput(
      nx    = c.downField("grid_nx").as[Int].toOption.getOrElse(64),
      ny    = c.downField("grid_ny").as[Int].toOption.getOrElse(32),
      steps = c.downField("steps_completed").as[Int].toOption.getOrElse(100),
      diag  = c.downField("diagnostics").as[RefDiag].toOption.getOrElse(
        throw new RuntimeException("Missing diagnostics")),
    )

  // ── Helpers ─────────────────────────────────────────────────────────────────

  private def pctErr(got: Double, ref: Double): Double =
    math.abs((got - ref) / ref) * 100.0

  // ── Tests ────────────────────────────────────────────────────────────────────

  test("diagnostics within +-5% of Python reference") {
    val ref = loadReference()
    val req = SimulationRequest(
      gridNx               = Some(ref.nx),
      gridNy               = Some(ref.ny),
      domainLx             = Some(1.0),
      domainLy             = Some(0.5),
      dt                   = Some(0.001),
      steps                = Some(ref.steps),
      reynoldsNumber       = Some(1000.0),
      velocityShear        = Some(1.0),
      perturbationAmplitude= Some(0.01),
      perturbationMode     = Some(2),
    )

    val result = physics.Solver.simulate(req)
    val got    = result.diagnostics

    println("--- Scala vs Python reference ---")
    println(f"kinetic_energy : got=${got.kineticEnergy}%.6f  ref=${ref.diag.kineticEnergy}%.6f  err=${pctErr(got.kineticEnergy, ref.diag.kineticEnergy)}%.2f%%")
    println(f"enstrophy      : got=${got.enstrophy}%.6f  ref=${ref.diag.enstrophy}%.6f  err=${pctErr(got.enstrophy, ref.diag.enstrophy)}%.2f%%")
    println(f"max_vorticity  : got=${got.maxVorticity}%.6f  ref=${ref.diag.maxVorticity}%.6f  err=${pctErr(got.maxVorticity, ref.diag.maxVorticity)}%.2f%%")
    println(f"divergence_rms : got=${got.divergenceRms}%.2e  ref=${ref.diag.divergenceRms}%.2e")

    pctErr(got.kineticEnergy, ref.diag.kineticEnergy) should be < 5.0
    pctErr(got.enstrophy,     ref.diag.enstrophy)     should be < 5.0
    got.divergenceRms                                  should be < 1e-10
  }

  test("output field shapes are correct") {
    val req = SimulationRequest(
      gridNx = Some(32), gridNy = Some(16),
      dt     = Some(0.001), steps = Some(5),
    )
    val result = physics.Solver.simulate(req)
    val n = 32 * 16
    result.uVelocity.length shouldBe n
    result.vVelocity.length shouldBe n
    result.vorticity.length shouldBe n
    result.pressure.length  shouldBe n
    result.tFinal            should be (0.005 +- 1e-9)
  }
