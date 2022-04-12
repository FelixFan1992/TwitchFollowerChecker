import json
import logging
import os
import sys
import requests
import csv
import datetime

from Context import Context
from User import User

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='loggings.log',
                    level=logging.DEBUG)


def check_subscribers():
    ctx = Context()

    auth_url = 'https://id.twitch.tv/oauth2/authorize'
    GET_PARAMS = {
        'scope': 'channel:read:subscriptions',
        'client_id': ctx.client_id,
        'redirect_uri': 'http://localhost:3000',
        'response_type': 'token'
    }
    r = requests.request('GET', url=auth_url, params=GET_PARAMS)
    print(r.headers)
    print(r.status_code)


def check_channel_emotes():
    ctx = Context()

    channel_emotes_url = 'https://api.twitch.tv/helix/chat/emotes'
    GET_PARAMS = {
        'broadcaster_id': ctx.to_id
    }
    r = requests.request('GET', url=channel_emotes_url, params=GET_PARAMS, headers={
        'Client-Id': ctx.client_id,
        'Authorization': 'Bearer {}'.format(ctx.access_token)
    })
    logging.info(json.dumps(r.json(), indent=2))


def check_followers():
    ctx = Context()

    follower_url = 'https://api.twitch.tv/helix/users/follows'
    GET_PARAMS = {
        'to_id': ctx.to_id,
        'first': 100,
        'after': ''
    }

    followers_map = {}
    while True:
        r = requests.request('GET', url=follower_url, params=GET_PARAMS, headers={
            'Client-Id': ctx.client_id,
            'Authorization': 'Bearer {}'.format(ctx.access_token)
        })
        json_data = r.json()

        for item in json_data['data']:
            user = User(item['from_id'], item['from_name'], item['followed_at'])
            followers_map[user.user_id] = user

        pagination = json_data['pagination']
        if not pagination:
            break
        GET_PARAMS['after'] = pagination['cursor']

    last_followers_file = ''
    for f in os.listdir('.'):
        if f.endswith('.csv') and f > last_followers_file:
            last_followers_file = f

    last_followers_map = {}
    if last_followers_file:
        with open(last_followers_file, 'r') as f:
            for line in f.readlines():
                user_info = line.strip().split(',', 3)
                user = User(user_info[1], user_info[0], user_info[2])
                last_followers_map[user.user_id] = user

    followed = {}
    unfollowed = {}
    for user_id, user in last_followers_map.items():
        if user_id not in followers_map:
            unfollowed[user_id] = user
    for user_id, user in followers_map.items():
        if user_id not in last_followers_map:
            followed[user_id] = user

    logging.info('followed:')
    if len(followed) == 0:
        logging.info('  None')
    else:
        for user_id, user in followed.items():
            logging.info('  {}: {} followed at {}'.format(user.name, user.user_id, user.followed_at))

    logging.info('unfollowed:')
    if len(unfollowed) == 0:
        logging.info('  None')
    else:
        for user_id, user in unfollowed.items():
            logging.info('  {}: {} followed at {}'.format(user.name, user.user_id, user.followed_at))

    time = datetime.datetime.now()
    filename = time.strftime('%Y-%m-%d %H:%M:%S') + '-followers.csv'
    with open(filename, 'w+') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        for user_id in sorted(followers_map.keys()):
            user = followers_map[user_id]
            writer.writerow(tuple([user.name, user.user_id, user.followed_at]))
    logging.info('there are currently {} followers. {} more than last time you checked.'.format(
        len(followers_map), len(followers_map) - len(last_followers_map)))
    logging.info('new file {} created.'.format(filename))


def main():
    if len(sys.argv) != 2:
        logging.fatal('Must provide a run mode in the arguments.')
        return

    OPTIONS = {
        'FOLLOWERS': check_followers,
        'CHANNEL_EMOTES': check_channel_emotes,
        'SUBSCRIBERS': check_subscribers
    }

    if sys.argv[1].upper() not in OPTIONS:
        logging.fatal('Run mode {} is not supported.'.format(sys.argv[1]))
        return
    OPTIONS[sys.argv[1].upper()]()
    logging.info('***************************************************************************\n')


if __name__ == '__main__':
    main()
