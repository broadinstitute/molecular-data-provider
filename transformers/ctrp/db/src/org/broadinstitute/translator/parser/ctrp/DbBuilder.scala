package org.broadinstitute.translator.parser.ctrp

import java.sql.DriverManager;
import java.sql.Connection
import java.sql.Statement

trait DbBuilder {
  
  protected val UNIQUE = true
  
  private var connection: Connection = null

  protected def createDB(database: String) {
    Class.forName("org.sqlite.JDBC")
    connection = DriverManager.getConnection("jdbc:sqlite:" + database)
    connection.setAutoCommit(false)
  }

  protected def executeUpdate(sql: String) {
    val stm = connection.createStatement()
    stm.executeUpdate(sql)
    stm.close()
  }

  def createIndex(table: String, column: String) {
    createIndex(table, column, false)
  }

  def createIndex(table: String, column: String, unique: Boolean) {
    createIndex(table + '_' + column, table, column, unique)
  }

  def createIndex(name: String, table: String, column: String, unique: Boolean = false) {
    val sql = unique match {
      case false => s"CREATE INDEX ${name}_IDX ON ${table} (${column})"
      case true  => s"CREATE UNIQUE INDEX ${name}_IDX ON ${table} (${column})"
    }
    executeUpdate(sql)
  }

  def f(str: String) = str match {
    case null => "NULL"
    case _    => "'" + str.replace("'", "''") + "'"
  }

  def f(str: Option[String]) = str match {
    case None      => "NULL"
    case Some(str) => "'" + str.replace("'", "''") + "'"
  }

  def commit() {
    connection.commit()
  }

  def close() = {
    commit()
    connection.close()
  }

}
