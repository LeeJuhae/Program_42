from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker, scoped_session
import requests

from msg_contents import *
from server import engine, auth_info_table, get_scale
# import datetime

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', minute='*/1')
def scale_cron():
	session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
	user_ls = session.query(auth_info_table).all()
	session.close()
	for user_id, access_token in user_ls:
		get_scale(token, user_id)

scheduler.start()


# if __name__ == "__main__":
	# scheduler.add_job(scale_cron, 'cron', minute="0,15,30,45")


# def create_cron(access_token, user_id):
# 	scheduler.add_job(scale_cron,'cron', minute="0,15,30,45", args=[access_token, user_id], id=user_id)

# def update_cron(access_token, user_id):
# 	scheduler.modify_job(user_id, args=[access_token, user_id])

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
