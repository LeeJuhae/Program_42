#import secret
REDIRECT_URI = "http://localhost:65010/callback"
CLIENT_ID="2451a2427184f294a2ec8809755643ddbee64c1603d20b152bc5afc343c3c2fa"
CLIENT_SECRET="846d0c3279a8eee15b55c571d55fb00f5123c856f6e014e8264c911f2a97a603"

import requests
import requests.auth
import urllib.parse
from flask import Flask, request, jsonify, current_app, abort
from sqlalchemy import create_engine, text, Table, Column, String, MetaData, ForeignKey

app = Flask(__name__)

@app.route('/')
def homepage():
	text = '<a href="%s">Authenticate with 42intra</a>'
	print(make_authorization_url())
	return text % make_authorization_url()

# @app.route('/')
def make_authorization_url():
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI,
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public projects profile elearning tig forum"
	return url

def get_token(code):
	post_data = {
		"grant_type": "authorization_code",
		"client_id" : CLIENT_ID,
		"client_secret" : CLIENT_SECRET,
		"code": code,
		"redirect_uri": REDIRECT_URI}
	response = requests.post("https://api.intra.42.fr/oauth/token",
							 data=post_data)
	token_json = response.json()
	return token_json["access_token"]

@app.route('/callback')
def reddit_callback():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	code = request.args.get('code')
	token = get_token(code)
	req_url = "https://api.intra.42.fr/v2/notes"
	headers = {"Authorization": "Bearer " + token}
	res = requests.get(req_url, headers=headers)

	connection.execute(t.insert(), user_id='lee',code=code,token=token)
	trans.commit()

	return "got a code! %s\n and token!" % code +"   "+token

if __name__ == '__main__':
	app.config.from_pyfile("config.py")
	engine = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
	meta = MetaData()
	t = Table(
		'auth', meta,
		Column('user_id',String(20), primary_key=True),
		Column('code', String(64)),
		Column('token',String(64)),
	)
	meta.create_all(engine)
	connection = engine.connect()
	trans = connection.begin()

	app.run(debug=True, port=65010)
