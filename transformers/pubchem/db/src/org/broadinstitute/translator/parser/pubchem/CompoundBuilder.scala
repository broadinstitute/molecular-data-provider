package org.broadinstitute.translator.parser.pubchem
import scala.language.reflectiveCalls

import org.broadinstitute.translator.xml._

class CompoundBuilder extends ParentBuilder {

  val tag = "PC-Compound"

  val idBuilder = new ChildBuilder("PC-Compound_id", new TextValueBuilder("PC-CompoundType_id_cid")) =>: children
  val propertiesBuilder = new SequenceBuilder[PropertyBuilder]("PC-Compound_props", "PC-InfoData") =>: children

  override def close() {
    for (id <- idBuilder.child.get) {
      try {
        val cid = id.toLong
        var properties = Map[String, String]()
        for (p <- propertiesBuilder.elements; if p.isDefined) {
          val key = p.nameBuilder.get.getOrElse("") + " " + p.label
          for (columnName <- DB().compoundColumnMap.get(key); if p.value != "") {
            properties += columnName -> p.value
          }
        }
        DB().insertCompound(cid, None, properties)
      }
      catch {
        case e: Exception => print("ERROR: @CID:" + id + " " + e.getMessage)
      }
    }
  }
}
