
from datetime import datetime, timedelta
import time
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler

def scale_cron(token):
	req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	headers = {"Authorization": "Bearer " + token}
	params = {
		"range[begin_at]" : str(datetime.utcnow()) + "," + str(datetime.utcnow() + timedelta(minutes=15))
	}
	res = requests.get(req_url, headers=headers, params=params)
	if len(res.json()) > 0:
		if 'correcteds' in res.json()[0].keys():
			print(1)

if __name__ == '__main__':
    token = "c2fbe8fc57381edf63881b82e79e8c779d9a6628e9e6333b8ae6010088f4eda0"
    scheduler = BackgroundScheduler()
    scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=[token])
    scheduler.start()
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
