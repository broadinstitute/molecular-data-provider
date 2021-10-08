package org.broadinstitute.translator.parser.pubchem.rdf

import java.io.File
import scala.io.Source

class TTLparser(file: File) {

  private var prefixes = Map[String, String]()

  def parse(f: List[Triple] => Unit) {

    var triples: List[Triple] = Nil
    val input = Source.fromFile(file)
    var rowNo = 0
    var prevTriple: Option[Triple] = None
    for (line <- input.getLines) {
      rowNo += 1
      if (line.startsWith("@prefix ")) {
        checkLine(rowNo, line)
        parsePrefix(line.substring(8, line.length - 2))
      }
      else {
        checkLine(rowNo, line, prevTriple.isDefined)
        if (line.endsWith(" ,")) {
          val triple = prevTriple ->: parseTripple(rowNo, line.substring(0, line.length - 2))
          triples = triple :: triples
          prevTriple = Some(triple)
        }
        if (line.endsWith(" .")) {
          val triple = prevTriple ->: parseTripple(rowNo, line.substring(0, line.length - 2))
          f(triple :: triples)
          triples = Nil
          prevTriple = None
        }
      }
    }
    input.close()
  }

  private def parsePrefix(line: String) {
    val row = line.split("\t")
    val prefix = row(0)
    val uri = row(1)
    //println("'" + prefix + "'='" + uri + "'")
    prefixes += prefix -> uri
  }

  private def parseTripple(rowNo: Int, line: String): Triple = {
    val row = line.split("\t")
    if (row.length != 3) {
      Console.err.println("WARNING(line " + rowNo + "): unexpected line end: " + line)
    }
    return Triple(row(0), row(1), row(2))
  }

  private def checkLine(rowNo: Int, line: String, cont: Boolean) {
    if (cont && !line.startsWith("\t\t")) {
      Console.err.println("WARNING(line " + rowNo + "): unexpected line start: " + line)
    }
    if (!(line.endsWith(" .") || line.endsWith(" ,"))) {
      Console.err.println("WARNING(line " + rowNo + "): unexpected line end: " + line)
    }
  }

  private def checkLine(rowNo: Int, line: String) {
    if (!line.endsWith(" .")) {
      Console.err.println("WARNING(line " + rowNo + "): unexpected line end: " + line)
    }
  }
}

object TTLparser {

  def apply(filename: String) = new TTLparser(new File(filename))

  def process(triples: List[Triple]) {
    println(triples)
  }
}