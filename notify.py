import json
import requests
import settings


def notify(message, mention=False):
    url = settings.slack_webhook_url
    user_id = settings.slack_user_id
    headers = {'content-type': 'application/json'}
    payload = {
        'text': f'<@{user_id}> {message}' if mention else f'{message}'
    }
    requests.post(url, data=json.dumps(payload), headers=headers)
