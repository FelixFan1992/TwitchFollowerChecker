import logging
import os
import requests


class Context:
    def __init__(self):
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.to_id = os.getenv('TO_ID')
        self.client_id = os.getenv('CLIENT_ID')

        POST_PARAMS = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        auth_url = "https://id.twitch.tv/oauth2/token"
        r = requests.request('POST', url=auth_url, params=POST_PARAMS)
        self.access_token = r.json()['access_token']

        logging.info('\n')
        logging.info('access_token={}'.format(self.access_token))
        logging.info('to_id={}'.format(self.to_id))
        logging.info('client_id={}'.format(self.client_id))
        logging.info('client_secret={}'.format(self.client_secret))
