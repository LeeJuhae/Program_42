
import datetime
import pytz
import time
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from slack import WebClient

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
	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	# req_url = "https://api.intra.42.fr/v2/users/juhlee/scale_teams"
	headers = {"Authorization": "Bearer " + access_token}
	params = {
		"range[begin_at]" : str(datetime.datetime.utcnow()) + "," + str(datetime.datetime.utcnow() + datetime.timedelta(minutes=15))
	}
	res = requests.get(req_url, headers=headers, params=params)
	# res = requests.get(req_url, headers=headers)
	if len(res.json()) > 0:
		if 'correcteds' in res.json()[0].keys():
			scale_dict = res.json()[0]
			scale_info = get_scale_info(scale_dict, access_token)
			send_scale_message(user_id, scale_info)
		else:
			# auth_request()
			# scale_cron(token)
			print("token expired")

if __name__ == '__main__':
    token = "3b357184eccbb17ed53ee688b065f04f57896e33035e8b89477ed81167b1f831"
    user_id = "U0138U104UR"
    scheduler = BackgroundScheduler()
    scheduler.add_job(scale_cron,'cron', second="*/10", args=[token, user_id])
    # scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=[token, user_id])
    scheduler.start()

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
