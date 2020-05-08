
from datetime import datetime, timedelta
import time
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler

def send_scale_message(user_id, scale_info):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	response = client.conversations_open(users=user_id)
	scale_text = ""
	for info in scale_info:


	client.chat_postMessage(channel=response['channel']['id'], text=scale_text, user=user_id)
	return ""

def scale_cron(token, user_id):
	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	headers = {"Authorization": "Bearer " + token}
	params = {
		"range[begin_at]" : str(datetime.utcnow()) + "," + str(datetime.utcnow() + timedelta(minutes=15))
	}
	res = requests.get(req_url, headers=headers, params=params)
	if len(res.json()) > 0:
		scale_dict = res.json()[0]
		if 'correcteds' in scale_dict.keys():
			scale_info = {}
			scale_info['평가할 동료'] = scale_dict['team']['name'].split("'")[0]
			send_scale_message(user_id, scale_info)

			# print(1)
		# else:
			# auth_request()
			# scale_cron(token)

if __name__ == '__main__':
    token = "c2fbe8fc57381edf63881b82e79e8c779d9a6628e9e6333b8ae6010088f4eda0"
	user_id = "U0138U104UR"
    scheduler = BackgroundScheduler()
    scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=[token, user_id])
    scheduler.start()
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
