
import datetime
import pytz
import time
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from slack import WebClient
from flask import Flask,request
import webbrowser
import urllib.parse
from sqlalchemy.sql import select, column

# import test_db

REDIRECT_URI = 'http://59fc5070.ngrok.io/callback'
CLIENT_ID="2451a2427184f294a2ec8809755643ddbee64c1603d20b152bc5afc343c3c2fa"
CLIENT_SECRET="846d0c3279a8eee15b55c571d55fb00f5123c856f6e014e8264c911f2a97a603"

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
def db_insert():
	user_id = request.args.get('user_id')
	# print("!!!user_id",user_id)
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
		call_addjob(token, user_id)
		return "got a code! %s\n And token is %s" % (code, token)
	else:
		return "Already token exist!"

def send_scale_message(user_id, scale_info):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	response = client.conversations_open(users=user_id)
	scale_text = ""
	for k,v in scale_info.items():
		scale_text += k
		scale_text += " : "
		scale_text += str(v)
		scale_text += "\n"
	client.chat_postMessage(channel=response['channel']['id'], text=scale_text, user=user_id)
	return ""

def get_location(user,access_token):
	params = {
		"filter[active]" : "true"
	}
	response = requests.get("https://api.intra.42.fr/v2/users/%s/locations?access_token=%s"%(user,access_token), params=params)
	if len(response.json()) > 0:
		return response.json()[0]['host']
	else:
		return 'Unavailable'

def get_scale_info(scale_dict, access_token):
	scale_info = {}
	user_name = scale_dict['team']['name'].split("'")[0]
	scale_info['평가할 동료'] = user_name
	begin_time = datetime.datetime.strptime(scale_dict['begin_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
	utc_timezone = pytz.timezone("UTC")
	seoul_timezone = pytz.timezone("Asia/Seoul")
	localize_timestamp = utc_timezone.localize(begin_time)
	local_time = localize_timestamp.astimezone(seoul_timezone)
	scale_info['시작시간'] = datetime.datetime.strftime(local_time, "%H시 %M분")
	scale_info['평가진행시간'] = int(scale_dict['scale']['duration'] / 60)
	scale_info['평가자리'] = get_location(user_name, access_token)
	scale_info['평가할 프로젝트'] = scale_dict["team"]["project_gitlab_path"].split("/")[-1]
	return scale_info


def scale_cron(access_token, user_id):
	# req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	req_url = "https://api.intra.42.fr/v2/users/juhlee/scale_teams"
	headers = {"Authorization": "Bearer " + access_token}
	params = {
		"range[begin_at]" : str(datetime.datetime.utcnow()) + "," + str(datetime.datetime.utcnow() + datetime.timedelta(minutes=15))
	}
	# res = requests.get(req_url, headers=headers, params=params)
	res = requests.get(req_url, headers=headers)
	if len(res.json()) > 0:
		if 'correcteds' in res.json()[0].keys():
			scale_dict = res.json()[0]
			scale_info = get_scale_info(scale_dict, access_token)
			send_scale_message(user_id, scale_info)
		else:
			# auth_request()
			# scale_cron(token)
			print("token expired")

from sqlalchemy import create_engine, text, Table, Column, String, MetaData
def db_conn():
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

	return t, connection, trans

global scheduler
global t
global connection
global trnas
def call_addjob(token, user_id):
	scheduler.add_job(scale_cron,'cron', second="*/10", args=[token, user_id])
	# scheduler.add_job(scale_cron,'cron', minute="*/5", args=[token, user_id])

if __name__ == '__main__':
	scheduler = BackgroundScheduler()
	scheduler.start()
	# call_addjob("3b357184eccbb17ed53ee688b065f04f57896e33035e8b89477ed81167b1f831","U0138U104UR")
	# app.run(debug=True, port=65010)

	try:
		t, connection, trans = db_conn()
		app.run(debug=True, port=65010, use_reloader=False)

	# 	while(True):
	# 		time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
		scheduler.shutdown()


