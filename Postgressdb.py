import npyscreen
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extensions import AsIs
from psycopg2 import connect
from psycopg2 import extras
import sys
import getpass

class PostgreSQL(object):
    def create(self, userName):
        con = None
        self.dbname = "postgres"
        self.user = userName
        self.con = connect(dbname = self.dbname , user = self.user)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("select * from pg_database where datname = %(dname)s", {'dname': self.dbname })
        answer = cur.fetchall()
        
        if len(answer) <= 0:
            PostgreSQL.cur.execute('CREATE DATABASE ' + dbname + " OWNER " + user)

        query = "CREATE TABLE IF NOT EXISTS cars ( ID   SERIAL PRIMARY KEY,  name varchar(80), model int, year int);"
        cur.execute(query)
        query = "CREATE TABLE IF NOT EXISTS states ( ID   SERIAL PRIMARY KEY,  name varchar(80), population int, capital varchar(80));"
        cur.execute(query)
        self.con.commit()
        cur.close()
    
    def list_all_tables(self, table_name):
        cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT table_name FROM information_schema.tables \
                    WHERE \
                    table_type = 'BASE TABLE' AND table_schema = 'public' \
                    ORDER BY table_type, table_name")
        answer = cur.fetchall()
        cur.close()
        return answer

    def view_table(self, table_name):
        cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT * FROM " + table_name
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        return rows
    
    def list_columns(self, table_name):
        cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT * FROM " + table_name + " LIMIT 0"
        cur.execute(query)
        colnames = [desc[0] for desc in cur.description]
        cur.close()
        return colnames
    
    def add_record(self, record_id, table_name, table_values, table_col, row_len):
        c = self.con.cursor()
        self.convert = None
        self.index = 1
        self.rowDict = {}
        self.id = str(record_id)
        while self.index < row_len:
            self.rowDict[str(table_col[self.index])] = str(table_values[self.index])
            self.index += 1
        
        keys = self.rowDict.keys()
        values = [ self.rowDict[k] for k in keys ]
        query = "INSERT INTO " + table_name + " ("
        for k in self.rowDict:
            query = query + k + ", "
        query = query[:-2]
        query = query + ") VALUES ("
        for k in self.rowDict:
            if isinstance( self.rowDict[k], ( int, long ) ):
                self.convert = int(self.rowDict[k])
            else:
                self.convert = str(self.rowDict[k])
            query = query + "'" + self.convert  + "', "
        query = query[:-2]
        query = query + ")"
        c.execute(query)
        self.con.commit()
        c.close()

    def add_table(self, table_name, table_col, col_len):
        c = self.con.cursor()
        self.convert = None

        query = "CREATE TABLE IF NOT EXISTS " + table_name + " ( ID SERIAL PRIMARY KEY, "
        for k in table_col:
            query = query + k + " varchar(80), "
        query = query[:-2]
        query = query + ")"
        c.execute(query)
        self.con.commit()
        c.close()


    def update_record(self, table_name, table_values, table_col, row_len):
        c = self.con.cursor()
        self.index = 1
        self.rowDict = {}
        self.id = str(table_values[0])
        while self.index < row_len:
            self.rowDict[str(table_col[self.index])] = str(table_values[self.index])
            self.index += 1
    
        keys = self.rowDict.keys()
        values = [ self.rowDict[k] for k in keys ]
        query = "UPDATE " + table_name + " SET "
        for k in self.rowDict:
            query = query+ k + "='" + self.rowDict[k]  + "', "
        query = query[:-2]
        query = query + " WHERE id = " + table_values[0]
        c.execute(query)
        self.con.commit()
        c.close()


    def delete_record(self, record_id,table_name ):
        c = self.con.cursor()
        query = "DELETE FROM " + table_name + " WHERE id=" + str(record_id)
        c.execute(query)
        self.con.commit()
        c.close()

    def list_all_records(self, table_name):
        c = self.con.cursor()
        c.execute('SELECT * from ' + table_name)
        records = c.fetchall()
        c.close()
        return records

    def get_record(self, record_id, table_name):
        c = self.con.cursor()
        query = "SELECT * from " + table_name + " WHERE id=" + str(record_id)
        c.execute(query)
        records = c.fetchall()
        c.close()
        return records[0]
