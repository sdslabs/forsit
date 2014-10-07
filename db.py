#! /usr/bin/python
#---------------------------------------------------------Import Modules----------------------------------------------------------------------#


try:
    import MySQLdb
except ImportError as exc:
    print("Error: failed to import settings module ({})".format(exc))

import os
from ConfigParser import ConfigParser
import math



#---------------------------------------------------------Read Config-------------------------------------------------------------------------#



config=ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config', 'config.cfg'))



#----------------------------------------------------------Functions--------------------------------------------------------------------------#




def connect(app_name):

    '''Open database connection and return conn object to perform database queries'''

    host=config.get(app_name,"host")
    user=config.get(app_name,"user")
    passwd=config.get(app_name,"passwd")
    db=config.get(app_name,"db")
    charset=config.get(app_name,"charset")
    use_unicode=config.get(app_name,"use_unicode")


    try:
        conn=MySQLdb.connect(host,user,passwd,db,charset=charset,use_unicode=use_unicode)
        return conn
    except MySQLdb.Error, e:
        print "ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1])
        return 0




def write(sql,cursor,conn):
    '''Perform insert and update operations on the databse.
       Need to pass the cursor object as a parameter'''
    try:
        cursor.execute(sql)
        conn.commit()
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN WRITE OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql




def read(sql,cursor):
    '''Perform read operations on the databse.
       Need to pass the cursor object as a parameter'''
    try:
        cursor.execute(sql)
        result=cursor.fetchall()
        return result
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN READ OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql



def truncate(table_name, cursor):
    sql = "TRUNCATE TABLE " + str(table_name)
    read(sql, cursor)


def drop(table_name, cursor):
    sql = "DROP TABLE IF EXISTS " + str(table_name)
    read(sql, cursor)


def check_column(table,column,cursor):
    '''Used to check if `column` exists in `table`
       Need to pass the cursor object as a parameter'''
    sql="SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND COLUMN_NAME =  '{}'".format(table,column)
    #print sql
    try:
        return cursor.execute(sql)
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN CHECK COLUMN OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql



def add_column(sql,cursor):
    '''Used to add columns into tables'''
    try:
        cursor.execute(sql)
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN ADD COLUMN OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql



def add_table(sql,cursor):
    '''Used to create a new table in the db'''
    try:
        cursor.execute(sql)
    except MySQLdb.ProgrammingError, e:
        print "ERROR %d IN ADD TABLE OPERATION: %s" % (e.args[0], e.args[1])
        print "LAST QUERY WAS: %s" %sql
