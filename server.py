import requests
import urllib.parse
import json
from flask import Flask, request, redirect, render_template
from sqlalchemy.orm import sessionmaker, scoped_session

from manage_db import *
from msg_contents import *
from slack_msg import *
import datetime

REDIRECT_URI = 'https://dry-shore-10386.herokuapp.com/callback'

app = Flask(__name__,template_folder="templates")
auth_info_table, engine = connect_db()

def get_token(code, user_id, is_update):
	post_data = {
		"grant_type": "authorization_code",
		"client_id" : os.environ['CLIENT_ID'],
		"client_secret" : os.environ['CLIENT_SECRET'],
		"code": code,
		"redirect_uri": REDIRECT_URI + "?user_id=%s" %user_id + "&update=" + is_update,
	}
	response = requests.post("https://api.intra.42.fr/oauth/token", data=post_data)
	token_json = response.json()
	if "access_token" in token_json.keys():
		return token_json["access_token"]
	else:
		print("Not Found access_token!")
		return None


def reregister(user_id):
	params = {
		"client_id": os.environ['CLIENT_ID'],
		"response_type": "code",
		"redirect_uri": REDIRECT_URI + "?user_id=%s" %user_id + "&update=true",
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public%20projects"
	send_register_btn(url, user_id, is_update=True)


@app.route('/register', methods=['POST'])
def register():
	user_id = request.form['user_id']
	params = {
		"client_id": os.environ['CLIENT_ID'],
		"response_type": "code",
		"redirect_uri": REDIRECT_URI + "?user_id=%s" %user_id + "&update=false",
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public%20projects"
	return send_register_btn(url, user_id, is_update=False)


@app.route('/callback')
def callback():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error

	user_id = request.args.get('user_id')
	code = request.args.get('code')
	is_update = request.args.get('update')

	token = get_token(code, user_id, is_update=is_update)
	if token == None:
		return render_template("token_error.html")

	global engine
	session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

	if is_update == "true":
		update_query = get_update_query(auth_info_table, user_id, token)
		session.execute(update_query)
		session.commit()
		session.close()

		send_register_update_msg(user_id)
		get_scale(token, user_id)
		return render_template("token_reissued.html")

	else:
		if session.query(auth_info_table).filter_by(user_id=user_id).all() == []:
			insert_query = get_insert_query(auth_info_table, user_id, token)
			session.execute(insert_query)
			session.commit()
			session.close()

			send_register_finish_msg(user_id)
			return render_template("token_issued.html")

		else:
			session.commit()
			session.close()
			return render_template("token_already.html")

def get_scale(access_token, user_id):
	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	headers = {"Authorization": "Bearer " + access_token}
	params = {
		"range[begin_at]" : str(datetime.datetime.utcnow()) + "," + str(datetime.datetime.utcnow() + datetime.timedelta(minutes=15))
	}
	res = requests.get(req_url, headers=headers, params=params)
	if len(res.json()) > 0:
		if str(type(res.json())) == "<class 'dict'>" and res.json()['error'] == 'Not authorized':
			session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
			update_query = get_update_query(auth_info_table, user_id, "")
			session.execute(update_query)
			session.commit()
			session.close()
			reregister(user_id)
		elif str(type(res.json())) == "<class 'list'>" and 'correcteds' in res.json()[0].keys():
			scale_dict = res.json()[0]
			scale_info = get_scale_info(scale_dict, access_token)
			send_scale_message(user_id, scale_info)

if __name__ == '__main__':
	try:
		app.run()
	except (KeyboardInterrupt, SystemExit):
		print("bye")
