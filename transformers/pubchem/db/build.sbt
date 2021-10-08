
scalaVersion     := "2.12.8"

name := "pubchem-db"
version := "0.1.0"

lazy val root = (project in file("."))

Compile / scalaSource := baseDirectory.value / "src"

mainClass in (Compile, run) := Some("org.broadinstitute.translator.parser.pubchem.PubChem")

libraryDependencies += "org.scala-lang.modules" %% "scala-parser-combinators" % "1.0.6"
libraryDependencies += "org.scala-lang.modules" %% "scala-xml" % "1.0.6"
libraryDependencies += "org.xerial" % "sqlite-jdbc" % "3.21.0"
libraryDependencies +=  "org.scalaj" %% "scalaj-http" % "2.4.2"
