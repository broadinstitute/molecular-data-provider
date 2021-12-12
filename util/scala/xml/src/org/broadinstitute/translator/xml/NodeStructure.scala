package org.broadinstitute.translator.xml

import java.util.zip.ZipEntry
import java.util.zip.ZipFile
import scala.collection.mutable.ListBuffer

import scala.io.Source

import scala.xml.pull.XMLEventReader
import scala.xml.pull.XMLEvent
import scala.xml.pull.EvElemStart
import scala.xml.pull.EvElemEnd
import scala.xml.pull.EvText
import scala.collection.mutable.TreeSet

object NodeStructure {

  private var currentNode = new NodeStructure("", None)

  def main(args: Array[String]) {
    if (args(0).endsWith(".zip")) {
      mainZip(args(0))
    } 
    else {
      mainFile(args(0))
    }
  }
  
  def mainZip(filename: String) {
    val zipFile = new ZipFile("V:/data/explore/translator/knowledgeSources/SMPDB/download/smpdb_sbml.zip")
    val entries = zipFile.entries()
    val rootNode = new NodeStructure("", None)
    while (entries.hasMoreElements) {
      val entry = entries.nextElement()
      println("Parsing " + entry)
      val source = Source.fromInputStream(zipFile.getInputStream(entry))(io.Codec("UTF-8"))
      currentNode = rootNode
      val xml = new XMLEventReader(source)
      xml.foreach(matchEvents)
    }
    println(currentNode.toString(0))
  }

  def mainFile(filename: String) {
    val xml = new XMLEventReader(Source.fromFile(filename))
    xml.foreach(matchEvents)
    println(currentNode.toString(0))
  }

  def matchEvents(event: XMLEvent): Unit = {

    event match {
      case EvElemStart(_, tag, attr, _) => currentNode = currentNode.child(tag, attr.asAttrMap.keys.toSeq)
      case EvElemEnd(_, tag)            => currentNode = currentNode.getParent
      case _                            =>
    }
  }

}

class NodeStructure(val tag: String, val parent: Option[NodeStructure]) {

  val attributes: TreeSet[String] = new TreeSet[String]

  val elements: ListBuffer[NodeStructure] = new ListBuffer[NodeStructure]

  def getParent = parent.getOrElse(this)

  def child(childTag: String, attr: Seq[String]): NodeStructure = {
    val child = elements.find(_.tag == childTag) match {
      case Some(child) => child
      case None        => add(new NodeStructure(childTag, Some(this)))
    }
    child.attributes ++= attr
    return child
  }

  def add(node: NodeStructure): NodeStructure = {
    elements += node
    return node
  }

  def echo(node: NodeStructure, echoTag: Boolean = true): NodeStructure = {
    for (parent <- node.parent) echo(parent, false)
    print(if (echoTag) "/" + node.tag + "\n" else "/..")
    node
  }

  def toString(depth: Int): String = {
    " " * depth + "<" + tag + attributes.map(" @" + _).mkString("") + ">\n" + elements.map(_.toString(depth + 2)).mkString("")
  }
}