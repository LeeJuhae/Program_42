#noti_bot
REDIRECT_URI = 'http://59fc5070.ngrok.io/callback'
CLIENT_ID="2451a2427184f294a2ec8809755643ddbee64c1603d20b152bc5afc343c3c2fa"
CLIENT_SECRET="846d0c3279a8eee15b55c571d55fb00f5123c856f6e014e8264c911f2a97a603"

import requests
import requests.auth
import urllib.parse
from flask import Flask,request, redirect
from sqlalchemy import create_engine, text, Table, Column, String, MetaData
from sqlalchemy.sql import select, column
import os
from slack import WebClient
import webbrowser
import cron

# @app.route('/register', methods=['POST'])
# def register():
# 	user_id = request.form['user_id']
# 	params = {
# 		"client_id": CLIENT_ID,
# 		"response_type": "code",
# 		"redirect_uri": REDIRECT_URI+"?user_id=%s" %user_id,
# 	}
# 	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public%20projects%20profile%20elearning%20tig%20forum"
# 	webbrowser.open(url)
# 	return ""

# @app.route('/auth_request')
# def auth_request():
# 	user_id = request.args.get('user_id')
# 	params = {
# 		"client_id": CLIENT_ID,
# 		"response_type": "code",
# 		"redirect_uri": REDIRECT_URI+"?user_id=%s" %user_id,
# 	}
# 	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public projects profile elearning tig forum"
# 	return redirect(url)

# def get_token(code, user_id):
# 	post_data = {
# 		"grant_type": "authorization_code",
# 		"client_id" : CLIENT_ID,
# 		"client_secret" : CLIENT_SECRET,
# 		"code": code,
# 		"redirect_uri": REDIRECT_URI+"?user_id=%s" %user_id,
# 	}
# 	response = requests.post("https://api.intra.42.fr/oauth/token",
# 							 data=post_data)
# 	token_json = response.json()
# 	if "access_token" in token_json.keys():
# 		return token_json["access_token"]
# 	else:
# 		print("Not Found access_token!")
# 		return None


# @app.route('/callback')
# def db_insert():
# 	user_id = request.args.get('user_id')
# 	# print("!!!user_id",user_id)
# 	error = request.args.get('error', '')
# 	if error:
# 		return "Error: " + error
# 	code = request.args.get('code')
# 	token = get_token(code, user_id)
# 	if token == None:
# 		return "Error : Not Found access_token "
# 	req_url = "https://api.intra.42.fr/v2/notes"
# 	headers = {"Authorization": "Bearer " + token}
# 	res = requests.get(req_url, headers=headers)
# 	query =select([t]).where(t.columns.user_id == '%s' %user_id)
# 	if connection.execute(query).fetchall() == []:
# 		connection.execute(t.insert(), user_id=user_id,token=token)
# 		trans.commit()
# 		cron.call_addjob(token, user_id)
# 		return "got a code! %s\n And token is %s" % (code, token)
# 	else:
# 		return "Already token exist!"

def db_conn():
	cron.app.config.from_pyfile("config.py")

	engine = create_engine(cron.app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
	meta = MetaData()
	t = Table(
		'auth', meta,
		Column('user_id',String(20), primary_key=True),
		Column('token',String(64)),
	)

	meta.create_all(engine)

	connection = engine.connect()

	trans = connection.begin()

	return t, connection, trans

# def get_all_users(table):
