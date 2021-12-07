package org.broadinstitute.translator.xml

import scala.collection.mutable.ArrayBuffer

class SequenceBuilder[T <: Builder](override val tag: String, val childrenTag: String)(implicit newT: String => T) extends Builder {

  val elements = ArrayBuffer[T]()

  override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = if (tag == childrenTag) {
    val elementBuilder = newT(childrenTag)
    elements.append(elementBuilder)
    Some(elementBuilder)
  }
  else None

  def foreach(f: T => Unit) = elements.foreach(f)
}

