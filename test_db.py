#noti_bot
REDIRECT_URI = 'http://c55194e1.ngrok.io/callback'
CLIENT_ID="8f45964ae9efeb4d7e19e73b66bf7335a1c878df4629c23e48164701d35e9468"
CLIENT_SECRET="e7f8f0ff740f3a26eb755f748c81cc36671922ae5bd70cf42b557ce4774f7633"

import requests
import requests.auth
import urllib.parse
from flask import Flask, request, jsonify, current_app, abort, redirect
from sqlalchemy import create_engine, text, Table, Column, String, MetaData
from sqlalchemy.sql import select, column
import os
from slack import WebClient
import webbrowser

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
	user_id = request.form['user_id']
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI+"?user_id=%s" %user_id,
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public%20projects%20profile%20elearning%20tig%20forum"
	webbrowser.open(url)
	return ""

@app.route('/auth_request')
def auth_request():
	user_id = request.args.get('user_id')
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI+"?user_id=%s" %user_id,
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public projects profile elearning tig forum"
	return redirect(url)

def get_token(code, user_id):
	post_data = {
		"grant_type": "authorization_code",
		"client_id" : CLIENT_ID,
		"client_secret" : CLIENT_SECRET,
		"code": code,
		"redirect_uri": REDIRECT_URI+"?user_id=%s" %user_id,
	}
	response = requests.post("https://api.intra.42.fr/oauth/token",
							 data=post_data)
	token_json = response.json()
	if "access_token" in token_json.keys():
		return token_json["access_token"]
	else:
		print("Not Found access_token!")
		return None

@app.route('/callback')
def reddit_callback():
	user_id = request.args.get('user_id')
	print("!!!user_id",user_id)
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	code = request.args.get('code')
	token = get_token(code, user_id)
	if token == None:
		return "Error : Not Found access_token "
	req_url = "https://api.intra.42.fr/v2/notes"
	headers = {"Authorization": "Bearer " + token}
	res = requests.get(req_url, headers=headers)
	query =select([t]).where(t.columns.user_id == '%s' %user_id)
	if connection.execute(query).fetchall() == []:
		connection.execute(t.insert(), user_id=user_id,token=token)
		trans.commit()
		return "got a code! %s\n And token is %s" % (code, token)
	else:
		return "Already token exist!"

if __name__ == '__main__':
	client = WebClient(token=os.environ['SLACK_TOKEN'])

	app.config.from_pyfile("config.py")
	engine = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
	meta = MetaData()
	t = Table(
		'auth', meta,
		Column('user_id',String(20), primary_key=True),
		Column('token',String(64)),
	)
	meta.create_all(engine)
	connection = engine.connect()
	trans = connection.begin()

	while True:
		app.run(debug=True, port=65010)
