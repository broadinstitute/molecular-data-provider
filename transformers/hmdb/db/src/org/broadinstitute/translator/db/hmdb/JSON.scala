package org.broadinstitute.translator.db.hmdb

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.module.scala.experimental.ScalaObjectMapper
import com.fasterxml.jackson.databind.DeserializationFeature;

object JSON {

  val mapper = new ObjectMapper() with ScalaObjectMapper

  mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
}
