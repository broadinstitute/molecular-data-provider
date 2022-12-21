package org.broadinstitute.translator.parser.pubchem.rdf

case class Triple(sub: String, predicate: String, obj: String) {

  def ->:(prev: Option[Triple]): Triple = prev match {
    case Some(triple) => Triple(triple.sub, triple.predicate, this.obj)
    case None => this
  }

}
