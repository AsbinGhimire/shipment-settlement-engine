import pymysql

pymysql.install_as_MySQLdb()

import MySQLdb
# Fake a modern mysqlclient version
MySQLdb.version_info = (2, 2, 4, 'final', 0)
MySQLdb.install_as_MySQLdb = lambda: None # prevent re-install
