import npyscreen
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extensions import AsIs
from psycopg2 import connect
from psycopg2 import extras
import sys
import getpass
from Postgressdb import *
from MySQLdbClass import *


#*********************************************************************************************************************
#                                           LoginForm()
#
#   A Form class to create a login page, the form will allow the user to enter the username, and select one of the 
#   databases ( PostgreSQL or MySQL ), then it will create a database object based on the user choice and add it to 
#   the main application interface.
#
#*********************************************************************************************************************
class LoginForm(npyscreen.ActionForm, npyscreen.SplitForm):
    CANCEL_BUTTON_TEXT = "EXIT"
    def create(self):
        self.nextrelx += 25
        self.nextrely += 2
        self.username = self.add(npyscreen.TitleFixedText, name = "Login with your database username and password")
        self.nextrely += 2
        self.nextrelx += 3
        self.username = self.add(npyscreen.TitleText, name = "Username: ")
        self.nextrely += 1
        self.Password = self.add(npyscreen.TitleText, name = "Password: ")
        self.nextrely += 7
        self.database = self.add(npyscreen.TitleSelectOne, name = "Choose One:",
            values = ["PostgreSQL Database", "MySQL Database"], scroll_exit = True)

    def on_ok(self):
        if ''.join(self.database.get_selected_objects()) == "PostgreSQL Database":
            self.parentApp.dbset.user = ''.join(self.username.value)
            self.parentApp.dbset.Password = ''.join(self.Password.value)
            self.parentApp.myDatabase = PostgreSQL()
            self.parentApp.myDatabase.create(self.parentApp.dbset.user)
            self.parentApp.dbset.dbSelection = 'PostgreSQL'
            self.parentApp.selectTables = self.parentApp.addForm('TABLESELECTION', DisplayTables, draw_line_at = 5)
            self.parentApp.switchForm('TABLESELECTION')
        if ''.join(self.database.get_selected_objects()) == "MySQL Database":
            self.parentApp.dbset.user = ''.join(self.username.value)
            self.parentApp.dbset.Password = ''.join(self.Password.value)
            self.parentApp.myDatabase = MySQLObject()
            self.parentApp.myDatabase.create(self.parentApp.dbset.user, self.parentApp.dbset.Password)
            self.parentApp.dbset.dbSelection = 'MySQL'
            self.parentApp.selectTables = self.parentApp.addForm('TABLESELECTION', DisplayTables, draw_line_at = 5)
            self.parentApp.switchForm('TABLESELECTION')

    def on_cancel(self): 
        self.parentApp.change_form(None)

#*********************************************************************************************************************
#                                           NewTableColNum and NewTable()
#
#   A Form class to allow the user to create and add new table to the database, the classes will allow the user to
#   enter the desired table name and number of columns in the table, then will let the user to add the column names
#   and save the result as a new table in the database. The classes will then change forms to display the new content
#   of the database in the Display window.
#
#*********************************************************************************************************************
class NewTableColNum(npyscreen.ActionForm, npyscreen.SplitForm):
    CANCEL_BUTTON_TEXT = "Back"
    def create(self):
        self.nextrelx += 30
        self.nextrely += 1
        self.header_text = self.add(npyscreen.TitleFixedText, name = self.parentApp.dbset.dbSelection + '  --  Create New Table')
        self.nextrely += 2
        self.nextrelx -= 27
        self.table_name = self.add(npyscreen.TitleText, name = "Table Name: ")
        self.nextrely += 1
        self.table_col = self.add(npyscreen.TitleText, name = "Columns: ")
    
    def on_ok(self):
        del self.parentApp.newTable
        self.parentApp.dbset.colNumber = ''.join(self.table_col.value)
        self.parentApp.dbset.tableName = ''.join(self.table_name.value)
        self.parentApp.newTable = self.parentApp.addForm('NEWTABLE', NewTable, draw_line_at = 5)
        self.parentApp.switchForm('NEWTABLE')
    def on_cancel(self):
        self.parentApp.switchFormPrevious()

class NewTable(npyscreen.ActionForm, npyscreen.SplitForm):
    CANCEL_BUTTON_TEXT = "Back"
    def create(self):
        self.responseValues = {}
        self.index = 0
        self.columnIncrement = ''
        self.colNum = int(self.parentApp.dbset.colNumber)
        self.nextrelx += 30
        self.nextrely += 1
        self.header_text = self.add(npyscreen.TitleFixedText, name = self.parentApp.dbset.dbSelection + '  --  Add Table Attributes')
        self.nextrely += 1
        self.nextrelx -= 27
        while self.index < self.colNum:
            self.columnIncrement = "Column # " + str(self.index+1) + ": "
            self.nextrely += 1
            self.responseValues[self.index] = self.add(npyscreen.TitleText, name = self.columnIncrement)
            self.index += 1

    def beforeEditing(self):
            self.name = "New Table: %s" % self.parentApp.dbset.tableName

    def on_ok(self):
        self.index = 0
        while self.index < self.colNum:
            self.parentApp.dbset.headers.append(self.responseValues[self.index].value)
            self.index += 1
        self.parentApp.myDatabase.add_table(self.parentApp.dbset.tableName, self.parentApp.dbset.headers, self.colNum)
        del self.parentApp.dbset.headers[:]
        self.parentApp.switchForm("TABLESELECTION")
    def on_cancel(self):
        self.parentApp.switchForm("TABLESELECTION")

#*********************************************************************************************************************
#                                           DBSettings()
#
#   A class to set the Application variables
#
#*********************************************************************************************************************

class DBSettings(object):
    def __init__(self):
        self.user = ''
        self.Password = ''
        self.tableName = ''
        self.dbSelection = ''
        self.colNumber = 0
        self.table_rows = []
        self.headers = []

#*********************************************************************************************************************
#                                           DBTables()
#
#   A data class to save the selected table and add an action to create a new table, the class will change Forms to
#   display the content of the selected table, or to create new table window.
#
#*********************************************************************************************************************

class DBTables(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(DBTables, self).__init__(*args, **keywords)
        self.add_handlers({
            "^N": self.when_new_table
        })
    def display_value(self, value):
        return "%s" % (value[0])
    
    def actionHighlighted(self, act_on_this, keypress):
        self.columns = []
        tableSelection = act_on_this[0]
        del self.parent.parentApp.TableForm
        self.parent.parentApp.TableForm = self.parent.parentApp.addForm("TESTDISPLAY", RecordListDisplay)
        self.parent.parentApp.dbset.tableName = tableSelection
        self.parent.parentApp.getForm('TESTDISPLAY').value = tableSelection
        self.parent.parentApp.switchForm('TESTDISPLAY')

    def getTablename():
        return tableSelection
    
    def when_new_table(self, *args, **keywords):
        self.parent.parentApp.createTableForm = self.parent.parentApp.addForm("CREATENEWTABLE", NewTableColNum, draw_line_at = 5)
        self.parent.parentApp.switchForm('CREATENEWTABLE')

#*********************************************************************************************************************
#                                           DisplayTables()
#
#   A Form class to display the content of the database (List all the tables), it creates a window with the list of
#   the selected database tables, and allow the user to highlight a table to display, it saves the selected table 
#   values and switch forms to dipslay the content of the table.
#
#*********************************************************************************************************************

class DisplayTables(npyscreen.ActionFormMinimal, npyscreen.SplitForm, npyscreen.FormWithMenus):
    OK_BUTTON_TEXT = "Back"

    def when_exit(self):
        self.parentApp.switchForm( None )
        
    def when_new_table(self):
        self.parentApp.createTableForm = self.parentApp.addForm("CREATENEWTABLE", NewTableColNum, draw_line_at = 5)
        self.parentApp.switchForm('CREATENEWTABLE')

    def when_exit_menu(self):
        self.parentApp.setNextFormPrevious()

    def create(self):
        self.menu = self.new_menu(name = "Table Actions")
    	self.menu.addItem("Create New Table", self.when_new_table, "^A")
        self.menu.addItem("Close Menu", self.when_exit_menu, "^C")
        self.menu.addItem("Exit Program", self.when_exit, "^E")

        self.nextrelx += 38
        self.nextrely += 1
        self.header_text = self.add(npyscreen.TitleFixedText, name = self.parentApp.dbset.dbSelection + '  --  Tables')
        self.nextrely += 2
        self.nextrelx -= 35
        self.prompt = self.add(npyscreen.TitleFixedText, name = "Please select a table: ")
        self.nextrelx += 2
        self.action = self.add(DBTables, name='Select Table', scroll_exit = True)

        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE]  = self.on_ok
        
    def beforeEditing(self):
        self.update_list()
        
    def update_list(self):
        if self.parentApp.dbset.dbSelection == 'PostgreSQL':
	    self.action.values = self.parentApp.myDatabase.list_all_tables(self.parentApp.dbset.tableName)
	    self.action.display()
        else:
            self.action.values = self.parentApp.myDatabase.list_all_tables(self.parentApp.dbset.tableName)
            self.action.display()
        
    def on_ok(self):
        self.parentApp.switchForm('MAIN')
        self.parentApp.switchFormNow()

class TableManipulation(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(TableManipulation, self).__init__(*args, **keywords)
        self.add_handlers({
            "^N": self.when_new_table
        })
    def display_value(self, value):
        return "%s" % value
    
    def actionHighlighted(self, act_on_this, keypress):
        selectedTableName = act_on_this[0]
        self.parent.parentApp.dbset.tableName = selectedTableName
    def when_new_table(self, *args, **keywords):
    	self.parent.parentApp.switchForm('TABLECOLUMNS')

#*********************************************************************************************************************
#                                           RecordList()
#
#   A class to create a record of the selected table content, the class control the actions performed on the record,
#   it inlcude the Add, Edit and delete actions the user want to perform on a highlighted row, it then calls the 
#   database fucntions for add, edit or delete and save the new result to the tables
#
#*********************************************************************************************************************

class RecordList(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super(RecordList, self).__init__(*args, **keywords)
        self.add_handlers({
            "^A": self.when_add_record,
            "^D": self.when_delete_record,
            "^E": self.when_exit
        })


    def display_value(self, vl):
        self.rowLength = len(vl)
        self.rowArray = []
        self.index = 1
        self.rowStr = ''
        self.columns = self.parent.parentApp.myDatabase.list_columns(self.parent.parentApp.dbset.tableName)
        while (self.index < self.rowLength):
            self.rowStr += self.safe_string(str(vl[self.index])) + "\t"
            self.index += 1
        return self.rowStr
    def actionHighlighted(self, act_on_this, keypress):
        record = self.parent.parentApp.myDatabase.get_record(act_on_this[0], self.parent.parentApp.dbset.tableName)
        index = 0
        for rowVal in record:
            self.parent.parentApp.dbset.table_rows.append(str(rowVal))
            index += 1
        del self.parent.parentApp.editForm
        self.parent.parentApp.editForm = self.parent.parentApp.addForm("EDITRECORDFM", EditRecord, draw_line_at = 5)
        self.parent.parentApp.getForm('EDITRECORDFM').value = act_on_this[0]
        self.parent.parentApp.switchForm('EDITRECORDFM')

    def when_add_record(self, *args, **keywords):
        del self.parent.parentApp.editForm
        self.parent.parentApp.editForm = self.parent.parentApp.addForm("EDITRECORDFM", EditRecord, draw_line_at = 5)
        self.parent.parentApp.getForm('EDITRECORDFM').value = None
        self.parent.parentApp.switchForm('EDITRECORDFM')

    def when_delete_record(self, *args, **keywords):
        self.parent.parentApp.myDatabase.delete_record(self.values[self.cursor_line][0], self.parent.parentApp.dbset.tableName)
        self.parent.update_list()

    def when_exit(self, *args, **keywords):
        self.parent.parentApp.switchFormPrevious()
    
    def on_cancel(self):
        self.parentApp.switchFormPrevious()

#*********************************************************************************************************************
#                                           RecordListDisplay()
#
#   A Form class to display all the passed in record values
#
#*********************************************************************************************************************

class RecordListDisplay(npyscreen.ActionFormMinimal, npyscreen.FormMutt):
    OK_BUTTON_TEXT = "Back"
    MAIN_WIDGET_CLASS = RecordList

    def beforeEditing(self):
        self.update_list()

    def update_list(self):
        self.wMain.values = self.parentApp.myDatabase.list_all_records(self.parentApp.dbset.tableName)
        self.wMain.display()

    def on_ok(self):
        self.parentApp.switchFormPrevious()

#*********************************************************************************************************************
#                                           EditRecord()
#
#   A class to edit the row content of a selected table, it gets the list of the table columns, populate the list
#   with the existing data, and allow the user to edit the cloumn values then save the content to the database table
#
#*********************************************************************************************************************
class EditRecord(npyscreen.ActionForm, npyscreen.SplitForm):
    CANCEL_BUTTON_TEXT = "Back"
    def create(self):
        self.value = None
        self.nextrelx += 25
        self.nextrely += 1
        self.header_text = self.add(npyscreen.TitleFixedText, name = self.parentApp.dbset.dbSelection + '  --  ' + self.parentApp.dbset.tableName + '  --  Editable Record')
        self.nextrelx -= 22
        self.responseValues = {}
        self.index = 1
        self.parentApp.dbset.headers = self.parentApp.myDatabase.list_columns(self.parentApp.dbset.tableName)
        self.colNum = len(self.parentApp.dbset.headers)
        if self.value:
            while self.index < self.colNum:
                self.responseValues[self.index]   = self.add(npyscreen.TitleText, name = str(self.parentApp.dbset.headers[self.index]), value = self.parentApp.dbset.table_rows[self.index])
                self.index += 1
        else:
            self.record_id = 0
            self.index = 0
            while self.index < self.colNum:
                self.parentApp.dbset.table_rows.append('')
                self.responseValues[self.index] = ''
		self.nextrely += 1
                self.index += 1
            self.index = 1
            
            while self.index < self.colNum:
                self.responseValues[self.index]   = self.add(npyscreen.TitleText, name = str(self.parentApp.dbset.headers[self.index]), value = self.parentApp.dbset.table_rows[self.index])
                self.index += 1
    def beforeEditing(self):
        if self.value:
            record = self.parentApp.myDatabase.get_record(self.value, self.parentApp.dbset.tableName)
            self.name = "Record id : %s" % record[0]
            self.record_id = record[0]
        else:
            self.name = "New Record"

    def on_ok(self):
        if self.record_id:
            self.index = 1
            while self.index < self.colNum:
                self.parentApp.dbset.table_rows[self.index] = ''.join(self.responseValues[self.index].value)
                self.index += 1
            self.parentApp.myDatabase.update_record(self.parentApp.dbset.tableName, self.parentApp.dbset.table_rows, self.parentApp.dbset.headers, self.colNum)
            del self.parentApp.dbset.table_rows[:]
            del self.parentApp.dbset.headers[:]
        else:
            self.index = 1
            while self.index < self.colNum:
                self.parentApp.dbset.table_rows[self.index] = ''.join(self.responseValues[self.index].value)
                self.index += 1
            self.parentApp.myDatabase.add_record(self.record_id, self.parentApp.dbset.tableName, self.parentApp.dbset.table_rows, self.parentApp.dbset.headers, self.colNum)
            del self.parentApp.dbset.table_rows[:]
            del self.parentApp.dbset.headers[:]
        self.parentApp.switchFormPrevious()
    def on_cancel(self):
        self.parentApp.switchFormPrevious()

#*********************************************************************************************************************
#                                           DatabasesApplication()
#
#   A class to create the application main interface, the class sets up the application variable settings and create
#   a database object to interact with based on the user database selection. it also holds the application forms.
#
#**********************************************************************************************************************
class DatabasesApplication(npyscreen.NPSAppManaged):
    def onStart(self):
    	npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        
    	self.dbset = DBSettings()
        self.editForm = ''
        self.newTableColNum = self.addForm("TABLECOLUMNS", NewTableColNum, draw_line_at = 5)
        self.newTable = ''
    	self.addForm("MAIN", LoginForm, name = "Database Application", draw_line_at = 14)
    	self.addForm("TABLESELECTION", DisplayTables, draw_line_at = 5)
        self.addForm("POSTGRES", RecordListDisplay, draw_line_at = 4)
    	self.TableForm = self.addForm("TESTDISPLAY", RecordListDisplay)

    # This function switches screens in the interface
    def change_form(self, name):
        self.switchForm(name)

if __name__ == '__main__':
    myApp = DatabasesApplication()
    myApp.run()
