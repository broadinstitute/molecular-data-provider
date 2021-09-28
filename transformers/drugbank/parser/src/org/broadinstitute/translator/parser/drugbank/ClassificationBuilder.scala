package org.broadinstitute.translator.parser.drugbank

import org.broadinstitute.translator.xml._

class ClassificationBuilder(val tag: String) extends Builder {

  private var children: List[TextValueBuilder] = Nil

  override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = {
    val builder = new TextValueBuilder(tag)
    children = builder :: children
    return Some(builder)
  }

  def foreach(f: TextValueBuilder => Unit) = children.foreach(f)
}
