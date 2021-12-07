package org.broadinstitute.translator.xml

import scala.collection.mutable.ArrayBuffer

trait ParentBuilder extends Builder {

  private val childrenList = ArrayBuffer[Builder]()

  val children = new AnyRef {
    def =>:[T <: Builder](child: T): T = {
      childrenList += child
      child
    }
  }

  override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = {
    for (child <- childrenList if child.matches(tag, attr)) {
      return Some(child)
    }
    return createBuilder(tag, attr)
  }
  
  def createBuilder(tag: String, attr: Map[String, String]): Option[Builder] = Some(new Ignore(tag))
}

