import os
import requests
import csv
import datetime


def check_followers():
    client_secret = os.getenv('CLIENT_SECRET')
    to_id = os.getenv('TO_ID')
    client_id = os.getenv('CLIENT_ID')

    POST_PARAMS = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    auth_url = "https://id.twitch.tv/oauth2/token"
    r = requests.request('POST', url=auth_url, params=POST_PARAMS)
    access_token = r.json()['access_token']

    print('access_token={}'.format(access_token))
    print('to_id={}'.format(to_id))
    print('client_id={}'.format(client_id))
    print('client_secret={}'.format(client_secret))

    follower_url = "https://api.twitch.tv/helix/users/follows"

    GET_PARAMS = {
        'to_id': to_id,
        'first': 100,
        'after': ''
    }

    followers_map = {}
    while True:
        r = requests.request('GET', url=follower_url, params=GET_PARAMS, headers={
            'Client-Id': client_id,
            'Authorization': 'Bearer {}'.format(access_token)
        })
        json = r.json()

        for item in json['data']:
            followers_map[item['from_id']] = item['from_name']

        pagination = json['pagination']
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
                user = line.strip().split(',', 2)
                last_followers_map[user[1]] = user[0]

    followed = {}
    unfollowed = {}
    for user_id, user_name in last_followers_map.items():
        if user_id not in followers_map:
            unfollowed[user_id] = user_name
    for user_id, user_name in followers_map.items():
        if user_id not in last_followers_map:
            followed[user_id] = user_name

    print()
    print("followed:")
    if len(followed) == 0:
        print('  None')
    else:
        for user_id, user_name in followed.items():
            print('  {}: {}'.format(user_name, user_id))
    print()

    print("unfollowed:")
    if len(unfollowed) == 0:
        print('  None')
    else:
        for user_id, user_name in unfollowed.items():
            print('  {}: {}'.format(user_name, user_id))
    print()

    time = datetime.datetime.now()
    filename = time.strftime('%Y-%m-%d %H:%M:%S') + '-followers.csv'
    with open(filename, 'w+') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        for user_id in sorted(followers_map.keys()):
            writer.writerow(tuple([followers_map[user_id], user_id]))
    print('there are currently {} followers. {} more than last time you checked.'.format(
        len(followers_map), len(followers_map) - len(last_followers_map)))
    print('new file {} created.'.format(filename))
    print()


if __name__ == '__main__':
    check_followers()
