name := """molecular-data-provider"""

version := "2.5.1"

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

val jacksonVersion         = "2.13.4"   // or 2.12.7
val jacksonDatabindVersion = "2.13.4.2" // or 2.12.7.1

val jacksonOverrides = Seq(
  "com.fasterxml.jackson.core"     % "jackson-core",
  "com.fasterxml.jackson.core"     % "jackson-annotations",
  "com.fasterxml.jackson.datatype" % "jackson-datatype-jdk8",
  "com.fasterxml.jackson.datatype" % "jackson-datatype-jsr310"
).map(_ % jacksonVersion)

val jacksonDatabindOverrides = Seq(
  "com.fasterxml.jackson.core" % "jackson-databind" % jacksonDatabindVersion
)

val akkaSerializationJacksonOverrides = Seq(
  "com.fasterxml.jackson.dataformat" % "jackson-dataformat-cbor",
  "com.fasterxml.jackson.module"     % "jackson-module-parameter-names",
  "com.fasterxml.jackson.module"     %% "jackson-module-scala",
).map(_ % jacksonVersion)

libraryDependencies ++= jacksonDatabindOverrides ++ jacksonOverrides ++ akkaSerializationJacksonOverrides