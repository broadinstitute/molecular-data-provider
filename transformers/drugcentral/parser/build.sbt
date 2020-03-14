
scalaVersion     := "2.12.8"

name := "drug-central-parser"
version          := "0.1.0"

lazy val root = (project in file("."))

Compile / scalaSource := baseDirectory.value / "src"


libraryDependencies += "com.fasterxml.jackson.core" % "jackson-databind" % "2.8.9"
libraryDependencies += "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.8.9"
libraryDependencies += "org.xerial" % "sqlite-jdbc" % "3.21.0"
