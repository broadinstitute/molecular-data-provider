package org.broadinstitute.translator.parser.pubchem.db

import java.sql.DriverManager
import java.sql.Statement
import java.sql.ResultSet

abstract class SQLite(filename: String) {

  Class.forName("org.sqlite.JDBC")
  private val connection = DriverManager.getConnection("jdbc:sqlite:" + filename)
  connection.setAutoCommit(false)

  def createIndex(table: String, column: String, nocase: Boolean = false) {
    val collateNocase = if (nocase) " COLLATE NOCASE" else ""
    val sql = s"CREATE INDEX ${table}__${column}_IDX ON ${table} (${column}${collateNocase})"
    executeUpdate(sql)

  }

  protected def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  protected def executeQuery(sql: String) = connection.createStatement().executeQuery(sql)

  protected def queryResults(sql: String): Iterable[ResultSet] = new Iterable[ResultSet] {

    private val stm = connection.createStatement()
    private val resultSet = stm.executeQuery(sql)

    override def iterator = new Iterator[ResultSet] {
      override def hasNext: Boolean = {
        val next = resultSet.next()
        if (! next){
          stm.close()
        }
        return next
      }
      override def next = resultSet
    }
  }

  def f(str: String) = str match {
    case null => "NULL"
    case _ => "'" + str.replace("'", "''") + "'"
  }

  def f(str: Option[String]) = str match {
    case None => "NULL"
    case Some(str) => "'" + str.replace("'", "''") + "'"
  }

  def commit() {
    connection.commit()
  }

  def close() = {
    connection.close()
  }
}
