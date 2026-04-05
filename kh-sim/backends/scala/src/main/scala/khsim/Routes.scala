package khsim

import cats.effect.IO
import io.circe.syntax.*
import org.http4s.*
import org.http4s.circe.*
import org.http4s.dsl.io.*
import org.typelevel.log4cats.Logger

import physics.Solver

object Routes:
  // EntityDecoder must be in implicit scope for req.as[SimulationRequest]
  // http4s as[A] signature: (MonadThrow[F], EntityDecoder[F, A]) — do NOT pass explicitly
  private given EntityDecoder[IO, SimulationRequest] = jsonOf[IO, SimulationRequest]

  def apply()(using logger: Logger[IO]): HttpRoutes[IO] =
    HttpRoutes.of[IO]:

      // ── POST /simulate ─────────────────────────────────────────────────────

      case req @ POST -> Root / "simulate" =>
        for
          body   <- req.as[SimulationRequest]
          _      <- logger.info(
                      s"simulate nx=${body.nx} ny=${body.ny} steps=${body.nSteps} Re=${body.re}")
          result <- IO.blocking(Solver.simulate(body))   // off the CE thread-pool
          _      <- logger.info(
                      s"done t=${result.tFinal} ke=${result.diagnostics.kineticEnergy} " +
                      s"ms=${result.computeTimeMs}")
          resp   <- Ok(result.asJson)
        yield resp

      // ── GET /health ────────────────────────────────────────────────────────

      case GET -> Root / "health" =>
        Ok(HealthResponse("ok", "scala-http4s", 8002).asJson)

      // ── GET /info ──────────────────────────────────────────────────────────

      case GET -> Root / "info" =>
        Ok(InfoResponse(
          backend     = "scala-http4s",
          language    = "Scala",
          framework   = "http4s 0.23 (Ember)",
          fftLibrary  = "JTransforms 3.1",
          port        = 8002,
          openapiSpec = "kh-sim/shared/api/openapi.yaml",
        ).asJson)
