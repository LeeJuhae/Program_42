# REDIRECT_URI = "https://www.naver.com"
import secret
REDIRECT_URI = "http://localhost:65010/callback"

from flask import Flask
app = Flask(__name__)

@app.route('/')
def homepage():
	text = '<a href="%s">Authenticate with 42intra</a>'
	print(make_authorization_url())
	return text % make_authorization_url()

def make_authorization_url():
	# from uuid import uuid4
	# state = str(uuid4())
	# save_created_state(state)
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI,
	}
	import urllib.parse
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public projects profile elearning tig forum"
	return url

import requests
import requests.auth
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

from flask import abort, request
@app.route('/callback')
def reddit_callback():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error
	# state = request.args.get('state', '')
	# if not is_valid_state(state):
		# Uh-oh, this request wasn't started by us!
		# abort(403)
	code = request.args.get('code')
	# We'll change this next line in just a moment
	token = get_token(code)
	req_url = "https://api.intra.42.fr/v2/notes"
	headers = {"Authorization": "Bearer " + token}
	# print(headers)
	res = requests.get(req_url, headers=headers)
	# f = open("a.txt","w")
	# f.write(res.text)
	# f.close()
	print(res.text)
	return "got a code! %s\n and token!" % code +"   "+token

if __name__ == '__main__':
	app.run(debug=True, port=65010)
