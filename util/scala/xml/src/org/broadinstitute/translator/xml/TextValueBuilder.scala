package org.broadinstitute.translator.xml

class TextValueBuilder(override val tag: String) extends Builder {

  private var value: Option[String] = None
  
  def setText(text: String){
    value = Some(text)
  }
  
  def get = value
  
  def text = value.getOrElse("")
  
  def textOption = value match {
    case Some(text) if text != "" => value
    case _ => None
  }
}

object TextValueBuilder {

  def apply(tag: String) = new TextValueBuilder(tag)
  
  implicit def createBuilder(tag: String) = TextValueBuilder(tag)
}

