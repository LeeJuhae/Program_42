from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.orm import sessionmaker, scoped_session
import requests

from msg_contents import *
from server import engine, auth_info_table, get_scale

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', minute='0,15,30,45')
def scale_cron():
	session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
	user_ls = session.query(auth_info_table).all()
	session.close()
	for user_id, access_token in user_ls:
		if access_token != "":
			get_scale(access_token, user_id)

scheduler.start()
