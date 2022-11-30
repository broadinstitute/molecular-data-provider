package org.broadinstitute.translator.db.hmdb

import scala.io.Source

import org.broadinstitute.translator.xml.Builder
import org.broadinstitute.translator.xml.Parser

object HMDBparser {

  private var count = 0

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
    override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = {
      count = count + 1
      if (count % 100 == 0) {
        println
        println(count)
        println("free memory:" + Runtime.getRuntime().freeMemory() / 1000000);
        print("/" + Runtime.getRuntime().totalMemory() / 1000000);
        println()
        DB.commit()
      }
      if (count % 1000 == 0) {
        DB.reconnect()
      }
      tag match {
        case "metabolite" => Some(new MetaboliteBuilder())
        case _ => None
      }
    }
  }
}
