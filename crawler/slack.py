import json
import requests


def slack_message(message):
    incoming_url = 'https://hooks.slack.com/services/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'
    post_data = {"text": '{}'.format(message)}
    data = json.dumps(post_data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
    requests.post(incoming_url, headers=headers, data=data)
    return None