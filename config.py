db = {
    'user'     : 'root',		# 1)
    'password' : '',		# 2)
    'host'     : 'localhost',	# 3)
    'port'     : 3306,			# 4)
    'database' : '42db'		# 5)
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
