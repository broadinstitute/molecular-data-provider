package org.broadinstitute.translator.parser.drugbank

import scala.io.Source

import org.broadinstitute.translator.xml.Builder
import org.broadinstitute.translator.xml.Parser

object DrugBankParser {

  def main(args: Array[String]){
    DB.createDB("DrugBank.sqlite")
    val source = Source.fromFile(args(0))(io.Codec("UTF-8"))
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
  
}
