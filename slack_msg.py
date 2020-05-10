import os
from slack import WebClient

# def register_finish_message(user_id):
def send_register_finish_msg(user_id):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_id = [user['id'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	response = client.conversations_open(users=user_id)
	client.chat_postMessage(channel=response['channel']['id'], blocks=[
			{
				"type":"divider"
			},
			{
				"type":"section",
				"text":{
					"type" : "mrkdwn",
					"text": ":tada: Connect finished!\n\n평가 시작 15분 전에 알려드릴게요. 편안히 코딩하세요 :pray:"
				},
			},
			{
				"type":"divider"
			}
			])
	return ""


# def register_update_message(user_id):
def send_register_update_msg(user_id):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	user_id = [user['id'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	response = client.conversations_open(users=user_id)
	client.chat_postMessage(channel=response['channel']['id'], blocks=[
			{
				"type":"divider"
			},
			{
				"type":"section",
				"text":{
					"type" : "mrkdwn",
					"text": ":tada: Token reissued!\n\n평가 시작 15분 전에 알려드릴게요. 편안히 코딩하세요 :pray:"
				},
			},
			{
				"type":"divider"
			}
			])
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


def send_register_btn(url, user_id, is_update):
	client = WebClient(token=os.environ['SLACK_TOKEN'])
	response = client.conversations_open(users=user_id)
	user_name = [user['real_name'] for user in client.users_list()['members'] if user['id'] == user_id][0]
	if is_update:
		message = ":exclamation: *Token expired* :exclamation:\nPlease update your intra access-token :)"
		button_text = "Update token"
	else:
		message = ":wave: Hello " + user_name + "!\nPlease connect with Intra account to get your evaluation info :)"
		button_text = "Connect Intra account"
	res = client.chat_postMessage(channel=response['channel']['id'], attachments=[
		{
			"color": "#000000",
			"blocks" : [
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": message
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
							"text": button_text
						},
						"style": "primary",
						"value": "click_me_123",
						"url" : url
					}
				]
			}]
		}]
	)
	return ""
