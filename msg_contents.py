import pytz
import datetime
import requests

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

