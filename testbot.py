import os
from slack import WebClient

# client = WebClient(token=slack_token)
client = WebClient(token=os.environ['SLACK_TOKEN'])

# slack_token="Bot User OAuth Access Token"

user_id = [user['id'] for user in client.users_list()['members'] if user['name'] == 'jushin'][0]
response = client.conversations_open(users=user_id)
client.chat_postMessage(channel=response['channel']['id'], text="Hello", user=user_id )
