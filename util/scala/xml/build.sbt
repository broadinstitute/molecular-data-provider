
scalaVersion     := "2.12.8"

name := "scala-xml-parser"
version          := "0.1.0"

lazy val root = (project in file("."))

Compile / scalaSource := baseDirectory.value / "src"

libraryDependencies += "org.scala-lang.modules" %% "scala-xml" % "1.0.6"