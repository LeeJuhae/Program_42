#noti_bot
REDIRECT_URI = "http://d2b3dab8.ngrok.io/callback"
CLIENT_ID="8f45964ae9efeb4d7e19e73b66bf7335a1c878df4629c23e48164701d35e9468"
CLIENT_SECRET="e7f8f0ff740f3a26eb755f748c81cc36671922ae5bd70cf42b557ce4774f7633"

import requests
import requests.auth
import urllib.parse
from flask import Flask, request, jsonify, current_app, abort, redirect
from sqlalchemy import create_engine, text, Table, Column, String, MetaData, ForeignKey

app = Flask(__name__)
import webbrowser

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
	print(token_json)
	return token_json["access_token"]


@app.route('/callback')
def reddit_callback():
	user_id = request.args.get('user_id')
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	code = request.args.get('code')
	token = get_token(code, user_id)
	req_url = "https://api.intra.42.fr/v2/notes"
	headers = {"Authorization": "Bearer " + token}
	res = requests.get(req_url, headers=headers)
	connection.execute(t.insert(), user_id=user_id,token=token)
	# connection.execute(t.update(),
	trans.commit()

	return "got a code! %s\n and token!" % code +"   "+token

import os
from slack import WebClient

# SLACK_TOKEN = "xoxb-1096950849861-1098346016706-VvuMrgVls6iRzohz48A6hY30"
# client = WebClient(token=slack_token)
# client = WebClient(token=os.environ['SLACK_TOKEN'])

# slack_token="Bot User OAuth Access Token"

# user_id = [user['id'] for user in client.users_list()['members'] if user['name'] == 'jushin'][0]
# response = client.conversations_open(users=user_id)
# client.chat_postMessage(channel=response['channel']['id'], text="Hello", user=user_id )

# def get_user(client):
# 	real_users = list()
# 	for user in client.users_list()['members']:
# 		if user['is_bot'] == False and user['real_name'] != 'Slackbot':
# 			real_users.append(user['id'])
# 	return (real_users)

if __name__ == '__main__':
	client = WebClient(token=os.environ['SLACK_TOKEN'])

	app.config.from_pyfile("config.py")
	engine = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
	meta = MetaData()
	t = Table(
		'auth', meta,
		Column('user_id',String(20), primary_key=True),
		# Column('code', String(64)),
		Column('token',String(64)),
	)
	meta.create_all(engine)
	connection = engine.connect()
	trans = connection.begin()

	# init_users = get_user(client)

	while 1:
		app.run(debug=True, port=65010)
