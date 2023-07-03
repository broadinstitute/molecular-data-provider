name := """molecular-data-provider"""

version := "2.4.3"

lazy val root = (project in file(".")).enablePlugins(PlayJava)

scalaVersion := "2.12.6"

libraryDependencies += "org.webjars" % "swagger-ui" % "3.32.5"
libraryDependencies += "javax.validation" % "validation-api" % "2.0.1.Final"
libraryDependencies += guice
libraryDependencies += filters

scalacOptions in (Compile, doc) += "-no-java-comments"

libraryDependencies += "com.auth0" % "java-jwt" % "3.18.1"
libraryDependencies += "com.auth0" % "jwks-rsa" % "0.19.0"
libraryDependencies += "org.apache.httpcomponents" % "httpclient" % "4.5.6"

