import os
from slack import WebClient
import json
from flask import Flask,request
app = Flask(__name__)

@app.route('/')
def homepage():
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_id = [user['id'] for user in client.users_list()['members'] if user['name'] == 'jushin'][0]
	response = client.conversations_open(users=user_id)
	client.chat_postMessage(channel=response['channel']['id'], text="Hello", user=user_id)
	return "send message"

@app.route('/register', methods=['POST'])
def register():
	challenge_code : json.loads(request.data.decode("UTF-8"))["challenge"]
	return {"challenge" : challenge_code}

if __name__ == '__main__':
	app.run(debug=True, port=65010)
