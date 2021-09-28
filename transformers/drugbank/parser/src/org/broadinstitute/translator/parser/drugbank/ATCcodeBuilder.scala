package org.broadinstitute.translator.parser.drugbank

import scala.collection.mutable.ArrayBuffer

import org.broadinstitute.translator.xml._


class ATCcodeBuilder(tag: String, attr: Map[String, String] = Map()) extends TextValueBuilder(tag) {

  val code = attr.get("code")

  val levels = ArrayBuffer[ATCcodeBuilder]()

  override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = if (tag == "level" || tag == "atc-code") {
    val levelBuilder = new ATCcodeBuilder(tag, attr)
    levels.append(levelBuilder)
    Some(levelBuilder)
  }
  else None

}