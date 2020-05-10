from slack import WebClient
import datetime
import requests

from msg_contents import *
from cron_test import *

def scale_cron(access_token, user_id):
	# req_url = "https://api.intra.42.fr/v2/me/scale_teams/as_corrector"
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_name = [user['real_name'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	req_url = "https://api.intra.42.fr/v2/users/" +user_name+"/scale_teams"

	headers = {"Authorization": "Bearer " + access_token}
	params = {
		"range[begin_at]" : str(datetime.datetime.utcnow()) + "," + str(datetime.datetime.utcnow() + datetime.timedelta(minutes=15))
	}
	# res = requests.get(req_url, headers=headers, params=params)
	res = requests.get(req_url, headers=headers)

	if len(res.json()) > 0:
		if str(type(res.json())) == "<class 'dict'>" and res.json()['error'] == 'Not authorized':
			# reissue_token(user_id)
			reregister(user_id)
		elif str(type(res.json())) == "<class 'list'>" and 'correcteds' in res.json()[0].keys():
			scale_dict = res.json()[0]
			scale_info = get_scale_info(scale_dict, access_token)
			send_scale_message(user_id, scale_info)
