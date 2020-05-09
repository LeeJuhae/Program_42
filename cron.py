import os
import pytz
import time
import datetime
import requests
import urllib.parse
from apscheduler.schedulers.background import BackgroundScheduler
from slack import WebClient
from flask import Flask, request, redirect
from sqlalchemy import create_engine, text, Table, Column, String, MetaData
from sqlalchemy.sql import select, column, insert, update
from sqlalchemy.orm import sessionmaker, scoped_session

REDIRECT_URI = 'http://257246c4.ngrok.io/callback'
CLIENT_ID="8f45964ae9efeb4d7e19e73b66bf7335a1c878df4629c23e48164701d35e9468"
CLIENT_SECRET="e7f8f0ff740f3a26eb755f748c81cc36671922ae5bd70cf42b557ce4774f7633"

global scheduler

app = Flask(__name__)

def register_finish_message(user_id):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_id = [user['id'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	response = client.conversations_open(users=user_id)
	client.chat_postMessage(channel=response['channel']['id'], text="%s register finish"%user_id, user=user_id)
	return ""


def register_update_message(user_id):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_id = [user['id'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	response = client.conversations_open(users=user_id)
	client.chat_postMessage(channel=response['channel']['id'], text="%s token update finish"%user_id, user=user_id)
	return ""


def send_scale_message(user_id, scale_info):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	response = client.conversations_open(users=user_id)
	scale_text = ":alarm_clock: :runner:  *평가가 왔어요*  :runner: :alarm_clock:\n\n"
	for i,(k,v) in enumerate(scale_info.items()):
		scale_text += k
		scale_text += " : *"
		scale_text += v
		scale_text += "*\n\n"
	client.chat_postMessage(
		channel=response['channel']['id'],
		blocks=[
			{"type":"divider"},
			{
				"type":"section",
				"text":{
					"type" : "mrkdwn",
					"text":scale_text
					},
			},
			{"type":"divider"}
			]
		)
	return ""


# def issue_token(register_url, user_id):
def send_register_btn(url, user_id):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	response = client.conversations_open(users=user_id)
	res = client.chat_postMessage(channel=response['channel']['id'], blocks=[
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Please authorize you"
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": True,
						"text": "Approve"
					},
					"style": "primary",
					"value": "click_me_123",
					"url" : url
				}
			]
		}
	])
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
	scale_info['시작 시간'] = datetime.datetime.strftime(local_time, "%H시 %M분")
	scale_info['평가진행 시간'] = str(int(scale_dict['scale']['duration'] / 60)) + "분"
	scale_info['평가 자리'] = get_location(user_name, access_token)
	scale_info['평가할 프로젝트'] = scale_dict["team"]["project_gitlab_path"].split("/")[-1]
	return scale_info


def get_update_query(table, user_id, token):
	update_query = update(table)
	update_query = update_query.values({"token": token})
	update_query = update_query.where(table.c.id == user_id)
	return update_query


def get_insert_query(table, user_id, token):
	insert_query = insert(table)
	insert_query = insert_query.values({"user_id":user_id, "token":token})
	return (insert_query)


def get_token(code, user_id, is_update):
	post_data = {
		"grant_type": "authorization_code",
		"client_id" : CLIENT_ID,
		"client_secret" : CLIENT_SECRET,
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


def reissue_token(user_id):
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI + "?user_id=%s" %user_id + "&update=true",
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public%20projects%20profile%20elearning%20tig%20forum"
	# issue_token(url, user_id)
	send_register_btn(url, user_id)
	# return ""


@app.route('/register', methods=['POST'])
def register():
	user_id = request.form['user_id']
	params = {
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI + "?user_id=%s" %user_id + "&update=false",
	}
	url = "https://api.intra.42.fr/oauth/authorize?" + urllib.parse.urlencode(params) + "&scope=public%20projects%20profile%20elearning%20tig%20forum"
	# return issue_token(register_url, user_id)
	return send_register_btn(url, user_id)


@app.route('/callback')
# def db_insert():
def control_db():
	error = request.args.get('error', '')
	if error:
		return "Error: " + error

	user_id = request.args.get('user_id')
	code = request.args.get('code')
	is_update = request.args.get('update')

	if is_update == "true":
		token = get_token(code, user_id, is_update="true")
		if token == None:
			return "Error : Not Found access_token "

		session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
		print("__session___ :",session)
		update_query = get_update_query(auth_info_table, user_id, code)
		session.execute(update_query)
		session.commit()

		register_update_message(user_id)
		scale_cron(token, user_id)

	else:
		token = get_token(code, user_id, is_update="false")
		if token == None:
			return "Error : Not Found access_token "

		session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
		print("__session___ :",session)

		if session.query(auth_info_table).filter_by(user_id=user_id).all() == []:
			insert_query = get_insert_query(auth_info_table, user_id, token)
			session.execute(insert_query)
			session.commit()

			call_addjob(token, user_id)
			register_finish_message(user_id)
			return "got a code! %s\n And token is %s" % (code, token)

		else:
			session.commit()
			return "Already token exist!"


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
		if str(type(res.json())) == "<class 'dict'>" and res.json()['error'] == 'Not authorized':
			reissue_token(user_id)
		elif str(type(res.json())) == "<class 'list'>" and 'correcteds' in res.json()[0].keys():
			scale_dict = res.json()[0]
			scale_info = get_scale_info(scale_dict, access_token)
			send_scale_message(user_id, scale_info)


def call_addjob(token, user_id):
	scheduler.add_job(scale_cron,'cron', second="*/10", args=[token, user_id])
	# scheduler.add_job(scale_cron,'cron', minute="*/5", args=[token, user_id])


def connect_db():
	app.config.from_pyfile("config.py")
	engine = create_engine(app.config['DB_URL'], encoding = 'utf-8', convert_unicode=False, pool_size=20, pool_recycle=500, max_overflow=20)

	meta = MetaData()
	auth_info_table = Table(
		'auth', meta,
		Column('user_id',String(20), primary_key=True),
		Column('token',String(64)),
	)
	meta.create_all(engine)

	return auth_info_table, engine


if __name__ == '__main__':
	scheduler = BackgroundScheduler()
	scheduler.start()
	# call_addjob("3b357184eccbb17ed53ee688b065f04f57896e33035e8b89477ed81167b1f831","U0138U104UR")
	# app.run(debug=True, port=65010)
	try:
		auth_info_table, engine = connect_db()
		# call_addjob("3b357184eccbb17ed53ee688b065f04f57896e33035e8b89477ed81167b1f831","U012M8XEHJB")
		app.run(debug=True, port=65010, use_reloader=False)

	# 	while(True):
	# 		time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
		scheduler.shutdown()
