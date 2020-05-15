from slack import WebClient
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import requests

from msg_contents import *
from server import *

scheduler = BackgroundScheduler()

def create_cron(access_token, user_id):
	scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=[access_token, user_id], id=user_id)

def update_cron(access_token, user_id):
	scheduler.modify_job(user_id, args=[access_token, user_id])

def scale_cron(access_token, user_id):
	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	headers = {"Authorization": "Bearer " + access_token}
	params = {
		"range[begin_at]" : str(datetime.datetime.utcnow()) + "," + str(datetime.datetime.utcnow() + datetime.timedelta(minutes=15))
	}
	res = requests.get(req_url, headers=headers, params=params)

	if len(res.json()) > 0:
		if str(type(res.json())) == "<class 'dict'>" and res.json()['error'] == 'Not authorized':
			reregister(user_id)
		elif str(type(res.json())) == "<class 'list'>" and 'correcteds' in res.json()[0].keys():
			scale_dict = res.json()[0]
			scale_info = get_scale_info(scale_dict, access_token)
			send_scale_message(user_id, scale_info)

scheduler.start()

# def scale_cron(access_token, user_id):
# 	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
# 	headers = {"Authorization": "Bearer " + access_token}
# 	params = {
# 		"range[begin_at]" : str(datetime.datetime.utcnow()) + "," + str(datetime.datetime.utcnow() + datetime.timedelta(minutes=15))
# 	}
# 	res = requests.get(req_url, headers=headers, params=params)

# 	if len(res.json()) > 0:
# 		if str(type(res.json())) == "<class 'dict'>" and res.json()['error'] == 'Not authorized':
# 			reregister(user_id)
# 		elif str(type(res.json())) == "<class 'list'>" and 'correcteds' in res.json()[0].keys():
# 			scale_dict = res.json()[0]
# 			scale_info = get_scale_info(scale_dict, access_token)
# 			send_scale_message(user_id, scale_info)
