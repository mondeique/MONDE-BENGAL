import random
import string
from web_crawler.loader import load_credential
import requests


def get_image_filename(image):
    _First = '_1'

    if image:
        whole_name = image.name
        jpg_name = whole_name.split('/')[1]
        prev_name = jpg_name.split('.')[0]
        name = prev_name.split('_')[0]
        name_order = int(prev_name.split('_')[1])
        next_order = name_order + 1
        rename = name + '_' + str(next_order) + '.jpg'
        print('renamed!')
        return rename
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) + \
           random.choice(string.ascii_uppercase) + _First + '.jpg'


def get_token():
    login_url = load_credential("MONDEBRO_URL") + '/api/auth/login'
    username = load_credential("MONDEBRO_USERNAME")
    password = load_credential("MONDEBRO_PASSWORD")
    data = {'username': username, 'password': password}
    token = requests.post(url=login_url, data=data).json()['token']
    return token


def valid_token(token):
    headers = {'Authorization': 'token {}'.format(token)}
    user_url = load_credential("MONDEBRO_URL")+'/api/auth/user'
    status = requests.get(url=user_url, headers=headers).status_code
    if status == 401:
        token = get_token()
        return token
    return token


def sync_mondebro(token, shop):
    token = valid_token(token)
    headers = {'Authorization': 'token {}'.format(token)}
    sync_url = load_credential("MONDEBRO_URL")+'/api/v1/sync/{}/'.format(shop)
    sync = requests.post(url=sync_url, headers=headers)
    return sync.status_code
