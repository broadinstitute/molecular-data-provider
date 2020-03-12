package org.broadinstitute.translator.xml

class ChildBuilder[T <: Builder](override val tag: String, val child: T) extends Builder {
  override def getBuilder(tag: String, attr: Map[String, String]): Option[Builder] = 
    if (child.matches(tag, attr)) Some(child) else None 
}

