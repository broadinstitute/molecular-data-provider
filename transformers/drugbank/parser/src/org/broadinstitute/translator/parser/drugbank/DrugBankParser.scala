package org.broadinstitute.translator.parser.drugbank

import scala.io.Source

import org.broadinstitute.translator.xml.Builder
import org.broadinstitute.translator.xml.Parser

object DrugBankParser {

  def main(args: Array[String]) {
    DB.createDB(args(0))
    val source = Source.fromFile(args(1))(io.Codec("UTF-8"))
    Parser.parse(source, new RootBuilder)
    DB.commit()
    DB.createIndexes()
    DB.commit()
    DB.close()
  }

  class RootBuilder extends Builder {
    val tag = ""
    override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = tag match {
      case "drug" => Some(new DrugBuilder(attr("type")))
      case _      => None
    }
  }

  import java.nio.file.{ Paths, Files }
  import java.nio.charset.StandardCharsets

  def main1(args: Array[String]) {
    val source = Source.fromFile(args(0))(io.Codec("UTF-8"))
    Files.write(Paths.get(args(0).substring(0, args(0).length() - 4) + "-test.xml"), source.take(3000000).mkString.getBytes(StandardCharsets.UTF_8))
    source.close()
  }

}
