
from datetime import datetime, timedelta
import time
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = "b96e97828dced9a10758efec502d8e7daeccfeef3e73dfbd391dc120bcf8c874"

def scale_cron():
	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	headers = {"Authorization": "Bearer " + TOKEN}
	params = {
		"range[begin_at]" : str(datetime.utcnow()) + "," + str(datetime.utcnow() + timedelta(minutes=15))
	}
	res = requests.get(req_url, headers=headers, params=params)
	if res.text == '[]':
		print(1)
	else:
		print(2)


if __name__ == '__main__':
    token_dict = {"token" : "b96e97828dced9a10758efec502d8e7daeccfeef3e73dfbd391dc120bcf8c874"}
    # token = "b96e97828dced9a10758efec502d8e7daeccfeef3e73dfbd391dc120bcf8c874"
    scheduler = BackgroundScheduler()
    scheduler.add_job(scale_cron,'cron', minute="11")
    scheduler.start()
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
