package org.broadinstitute.translator.xml

import scala.io.Source
import scala.collection.mutable.Stack

import scala.xml.pull.XMLEventReader
import scala.xml.pull.XMLEvent
import scala.xml.pull.EvElemStart
import scala.xml.pull.EvElemEnd
import scala.xml.pull.EvText

object Parser {

  val builderStack: Stack[Builder] = Stack()

  def parse(source: Source, rootBuilder: Builder) {
    builderStack push rootBuilder
    val xml = new XMLEventReader(source)
    xml.foreach(matchEvents)
  }

  def matchEvents(event: XMLEvent): Unit = {

    event match {
      case EvElemStart(_, tag, attr, _) => for (builder <- builderStack.top.getBuilder(tag, attr.asAttrMap)) {
        builderStack push builder
        if (builder.isInstanceOf[Attributes]) builder.asInstanceOf[Attributes] setAttributes attr.asAttrMap
      }
      case EvText(text) if builderStack.top.isInstanceOf[TextValueBuilder] => builderStack.top.asInstanceOf[TextValueBuilder] setText text
      case EvElemEnd(_, tag) if tag == builderStack.top.tag => builderStack.pop.close()
      case _ =>
    }
  }

}