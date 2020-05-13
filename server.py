import requests
import urllib.parse
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, redirect, render_template
from sqlalchemy.orm import sessionmaker, scoped_session

from manage_db import *
from msg_contents import *
from slack_msg import *
from cron import *

REDIRECT_URI = 'http://0118302f.ngrok.io/callback'

global scheduler

app = Flask(__name__,template_folder="templates")
# app.config.from_pyfile("config.py")

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

	session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

	if is_update == "true":

		update_query = get_update_query(auth_info_table, user_id, code)
		session.execute(update_query)
		session.commit()
		session.close()

		send_register_update_msg(user_id)
		scale_cron(token, user_id)
		scheduler.modify_job(user_id, args=[token, user_id])
		return render_template("token_reissued.html")

	else:
		if session.query(auth_info_table).filter_by(user_id=user_id).all() == []:
			insert_query = get_insert_query(auth_info_table, user_id, token)
			session.execute(insert_query)
			session.commit()
			session.close()

			scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=[token, user_id], id=user_id)
			send_register_finish_msg(user_id)
			return render_template("token_issued.html")

		else:
			session.commit()
			session.close()
			return render_template("token_already.html")


if __name__ == '__main__':
	scheduler = BackgroundScheduler()
	scheduler.start()
	scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=["32551b45f6003b14ca54995f023f8043379ea004cfa212632f2fc561169d5c22", "U013CE0B23C"], id="U013CE0B23C")
	scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=["46ac2d041776f168224a8fa340529b0fc7e5ed6a0dd8ec95b1e27257ccc0b19e", "U013JKBRKQC"], id="U013JKBRKQC")

	try:
		auth_info_table, engine = connect_db(app)
		app.run(debug=True, port=65010, use_reloader=False)
	except (KeyboardInterrupt, SystemExit):
		scheduler.shutdown()
