name := """gelinea-transformer"""

version := "2.0.0"

lazy val root = (project in file(".")).enablePlugins(PlayJava)

.settings(PlayKeys.playDefaultPort := 8290)

scalaVersion := "2.12.2"

libraryDependencies += "org.webjars" % "swagger-ui" % "3.1.5"
libraryDependencies += "javax.validation" % "validation-api" % "1.1.0.Final"
libraryDependencies += guice
libraryDependencies += filters

scalacOptions in (Compile, doc) += "-no-java-comments"
