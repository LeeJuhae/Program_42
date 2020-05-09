import os
from slack import WebClient
import json
import urllib.parse
import requests
from flask import Flask,request
import webbrowser
app = Flask(__name__)

CLIENT_ID = "2451a2427184f294a2ec8809755643ddbee64c1603d20b152bc5afc343c3c2fa"
CLIENT_SECRET = "846d0c3279a8eee15b55c571d55fb00f5123c856f6e014e8264c911f2a97a603"
REDIRECT_URI = "http://e5630b3d.ngrok.io/callback"


@app.route('/')
def homepage():
	return "homepage"

@app.route('/register', methods=["POST"])
def register():
	user_id = request.form['user_id']
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI + "?user_id=%s" % user_id,
	}
	url = "https://api.intra.42.fr/oauth/authorize?scope=public%20projects%20profile%20elearning%20tig%20forum&" + urllib.parse.urlencode(params)
	webbrowser.open(url)
	return ""

def send_message(user_id):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_id = [user['id'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	response = client.conversations_open(users=user_id)
	client.chat_postMessage(channel=response['channel']['id'], text="%s register finish"%user_id, user=user_id)
	return ""

def get_token(code, user_id):
	post_data = {
		"grant_type": "authorization_code",
		"client_id" : CLIENT_ID,
		"client_secret" : CLIENT_SECRET,
		"code": code,
		"redirect_uri": REDIRECT_URI + "?user_id=%s" % user_id,
		}
	response = requests.post("https://api.intra.42.fr/oauth/token",
							 data=post_data)
	token_json = response.json()
	if "access_token" in token_json.keys():
		return token_json["access_token"]
	else:
		print(token_json)
		return None

@app.route('/callback')
def code_callback():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	code = request.args.get('code')
	user_id = request.args.get('user_id')
	token = get_token(code,user_id)
	print(token)
	# db저장
	send_message(user_id)
	return "Finish registration!!\nNow we will notify you before evaluation starts 15 minutes"
	# return "got a code! %s\n and token!" % code + "   "+ token

if __name__ == '__main__':
	app.run(debug=True, port=65010)
