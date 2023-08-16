
scalaVersion     := "2.12.8"

name := "molepro-db"
version := "2.3.0"

lazy val root = (project in file("."))

Compile / scalaSource := baseDirectory.value / "src"
Compile / unmanagedJars := (baseDirectory.value / "lib" * "*.jar").classpath

mainClass in (Compile, run) := Some("org.broadinstitute.translator.moleprodb.builder.MoleProDBBuilder")

libraryDependencies += "org.xerial" % "sqlite-jdbc" % "3.8.11.2"

lazy val createDB = taskKey[Unit]("Create new MolePro database.")

fullRunTask(createDB, Compile, "org.broadinstitute.translator.moleprodb.builder.MoleProDBBuilder", "data/db/MoleProDB.sqlite", "exec", "../schema/MoleProSchema.sql")

