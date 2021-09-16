package org.broadinstitute.translator.xml

trait Builder {

  def tag: String

  def matches(tag: String, attr: Map[String, String]): Boolean = this.tag == tag
  
  def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = None // get a builder for a child with a tag

  def close(): Unit = {}

}

class Ignore(override val tag: String) extends Builder {
  
}

trait Attributes {
  
  private var _attr: Map[String, String] = Map()
  
  def attr = _attr
  
  def setAttributes(attr: Map[String, String]) = {
    if (_attr.size == 0) _attr = attr
  }

}