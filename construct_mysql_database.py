#!/usr/bin/env python
# construct_mysql_database.py
# 2013-05-19 
# William Wu 

# import packages
import sys, getopt, MySQLdb, getpass
from ConfigParser import SafeConfigParser as Parser

# usage
def usage():
    print('Usage:\n\t%s -h [hostname] -d [dbname] -u [username] -t [tablename]' % sys.argv[0])
    print('Options:')
    print('\t%-20s %-30s' % ("-h [hostname]", "hostname; defaults to localhost"))
    print('\t%-20s %-30s' % ("-u [username]", "username; defaults to root"))
    print('\t%-20s %-30s' % ("-t [tablename]", "table name; required"))
    print('\t%-20s %-30s' % ("-d [dbname]", "database name; required"))
    print('\t%-20s %-30s' % ("-y", "forces a 'yes' answer to all user prompts"))
    print('Example:')
    print('\t%s -c db.conf' % sys.argv[0])
    print('Note:')
    print('\tPassword will be prompted if config file is not supplied.')

# Configuration
def read_config(conf_file):
    conf = Parser()
    try: conf.read(conf_file)
    except: 
        print('Cannot read config file %s.' % conf_file) 
        sys.exit(-1)        
    try:         
        db_hostname = conf.get('database', 'hostname')
        db_username = conf.get('database', 'username')
        db_password = conf.get('database', 'password')
        db_dbname = conf.get('database', 'dbname')
        db_tablename = conf.get('database', 'tablename')
    except: 
        sys.exit("Bad config file, cannot proceed.")
    else:
        return (db_hostname, db_username, db_password, db_dbname, db_tablename)

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

# check that an argument has been provided
if len(sys.argv) < 2:
    usage()
    sys.exit()

# main method
def main(argv):

    # defaults
    username = "root"
    hostname = "localhost"
    dbname = None
    tablename = None
    configname = None
    password = None
    yes_flag = False

    # command-line arguments
    try:
        # gnu_getopt allows interspersing of option and non-option arguments
        opts, args = getopt.gnu_getopt(argv, "?u:d:h:t:c:y", ["help", "username=","dbname=","hostname=","tablename=","config=","yes"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-?", "--help"):
            usage()
            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-d", "--dbname"):
            dbname = arg
        elif opt in ("-h", "--hostname"):
            hostname = arg
        elif opt in ("-t", "--tablename"):
            tablename = arg
        elif opt in ("-c", "--config"):
            configname = arg
        elif opt in ("-y", "--yes"):
            yes_flag = True

    if None == tablename and not configname:
        print "Please supply a table name using the -t option."
        sys.exit()
    if None == dbname and not configname:
        print "Please supply a database name using the -d option."
        sys.exit()

    if configname:
        hostname, username, password, dbname, tablename = read_config(configname)

    # print input parameters
    print "Hostname: %s" % hostname
    print "Database: %s" % dbname
    print "Username: %s" % username
    print "Tablename: %s" % tablename

    # ask for password
    if not password:
        password = getpass.getpass()        

    # CREATE DATABASE
    # confirm user choice
    if not yes_flag:
        query_yes_no("Proceed to DROP database %s, if it exists?" % dbname)
    # establish connection
    conn = MySQLdb.connect (host = hostname,
                            user = username,
                            passwd = password)
    cursor = conn.cursor ()
    # sanity check
    cursor.execute ("SELECT VERSION()")
    row = cursor.fetchone ()
    print "server version:", row[0]
    # create
    cursor.execute ("DROP DATABASE IF EXISTS %s" % dbname)
    cursor.execute ("CREATE DATABASE %s" % dbname)
    # close connection
    cursor.close ()
    conn.close ()

    # CREATE TABLE
    # confirm user choice
    if not yes_flag:
        query_yes_no("Proceed to DROP table %s, if it exists?" % tablename)
    # establish connection
    conn = MySQLdb.connect (host = hostname,
                            user = username,
                            db = dbname,
                            passwd = password)
    cursor = conn.cursor ()
    # create table
    cursor.execute ("DROP TABLE IF EXISTS %s;" % tablename) # drop if table exists already
    cursor.execute ("CREATE TABLE %s ( id INTEGER AUTO_INCREMENT, i INTEGER, j INTEGER, k INTEGER, modified DATETIME, PRIMARY KEY (id));" % tablename)
    # confirm creation
    cursor.execute ("DESC %s;" % tablename)
    for row in cursor: print row
    # close connection
    cursor.close ()
    conn.close ()
    # done
    print "Finished constructing table '%s' inside MySQL database '%s'." % (tablename,dbname)

# invoke main
if __name__ == "__main__":
    main(sys.argv[1:])
