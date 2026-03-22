ThisBuild / name := "hello-test"
ThisBuild / version := "0.1.0"
ThisBuild / scalaVersion := "2.13.12"
ThisBuild / organization := "com.vibecodeprojects"
ThisBuild / organizationName := "VibeCodeProjects"

lazy val root = (project in file("."))
  .settings(
    name := "hello-test",
    version := "0.1.0",
    scalaVersion := "2.13.12",
    libraryDependencies += "org.scalatest" %% "scalatest" % "3.2.17" % Test,
    testFrameworks += new TestFramework("org.scalatest.tools.Framework"),
    scalacOptions ++= Seq(
      "-encoding", "UTF-8",
      "-target:jvm-11",
      "-deprecation",
      "-feature",
      "-unchecked",
      "-Xlog-reflective-calls",
      "-Ywarn-unused:imports"
    ),
    javacOptions ++= Seq(
      "-encoding", "UTF-8",
      "-source", "11",
      "-target", "11"
    )
  )
