import sys
import getpass
from subprocess import call
import MySQLdb
import os
import npyscreen

class MySQLObject(object):
    def create(self, userName, passwd):
        self.con = None
        self.dbname = "mysql"
        self.user = userName
        self.Password = passwd
        # Conenct to the default MySQL and create a temp database and change databases to the temp db
        self.con = MySQLdb.connect(host='127.0.0.1', user='root', passwd=self.Password, db=self.dbname)
        cur = self.con.cursor()
        # Check if the database exist in the database
        exeCur = cur.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'TESTDB'")
        if exeCur == 1:
            print "database Exists!!\n"
        else:
            exeCur = cur.execute("CREATE DATABASE IF NOT EXISTS TESTDB")

        exeCur = cur.execute("USE TESTDB")

        # Check if a user exist in the database
        exeCur = cur.execute("SELECT 1 FROM mysql.user WHERE user=\'"+ self.user + "\'");
        if exeCur == 1:
            print " User exist in the database \n"
        else:
            #npyscreen.notify_confirm("User Does Not exist in the database!")
            # Create a new user
            query = "GRANT ALL ON TESTDB.* To '" + self.user + "'@'localhost' IDENTIFIED BY '" + self.Password + "'"
            exeCur = cur.execute(query)
            Message =  "Created new user " + self.user + "With the password = " + self.Password
        cur.close()

        # Connect with the user credintials
        self.con = MySQLdb.connect(host='127.0.01', user=self.user, passwd=self.Password, db='TESTDB')
        cur = self.con.cursor()

        query = "CREATE TABLE IF NOT EXISTS Employee ( ID   SERIAL PRIMARY KEY, Firstname varchar(80), Lastname varchar(80), Position varchar(80), Age int);"
        cur.execute(query)
        query = "CREATE TABLE IF NOT EXISTS Project ( ID   SERIAL PRIMARY KEY,  Name varchar(80), ManagerName varchar(80), Workers int);"
        cur.execute(query)
        query = "CREATE TABLE IF NOT EXISTS Products ( ID   SERIAL PRIMARY KEY,  Name varchar(80),  Quantity int);"
        cur.execute(query)
        self.con.commit()
        cur.close()
    
    def list_all_tables(self, table_name):
        cur = self.con.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'TESTDB'")
        answer = cur.fetchall()
        cur.close()
        return answer

    def view_table(self, table_name):
        cur = self.con.cursor()
        query = "SELECT * FROM " + table_name
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        return rows
    
    def list_columns(self, table_name):
        cur = self.con.cursor()
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
