import os
import requests
import csv
import datetime


def check_followers():
    URL = "https://api.twitch.tv/helix/users/follows"
    access_token = os.environ['TOKEN']
    to_id = os.environ['TO_ID']
    client_id = os.environ['CLIENT_ID']

    PARAMS = {
        'to_id': to_id,
        'first': 100,
        'after': ''
    }

    followers = []
    while True:
        r = requests.request('GET', url=URL, params=PARAMS, headers={
            'Authorization': 'Bearer {}'.format(access_token),
            'Client-Id': client_id
        })
        json = r.json()

        for item in json['data']:
            followers.append((item['from_name'], item['from_id']))

        pagination = json['pagination']
        if not pagination:
            break
        PARAMS['after'] = pagination['cursor']

    last_followers_file = ''
    for f in os.listdir('.'):
        if f.endswith('.csv') and f > last_followers_file:
            last_followers_file = f

    last_followers_list = []
    if last_followers_file:
        with open(last_followers_file, 'r') as f:
            for line in f.readlines():
                last_followers_list.append(tuple(line.strip().split(',', 2)))

    followed = []
    unfollowed = []
    for f in last_followers_list:
        if f not in followers:
            unfollowed.append(f)
    for f in followers:
        if f not in last_followers_list:
            followed.append(f)

    print("followed:" + ', '.join(str(f) for f in followed))
    print("unfollowed:" + ', '.join(str(f) for f in unfollowed))

    followers.sort(key=lambda x: x[1])
    time = datetime.datetime.now()
    filename = time.strftime('%Y-%m-%d %H:%M:%S') + '-followers.csv'
    with open(filename, 'w+') as f:
        writer = csv.writer(f)
        for item in followers:
            writer.writerow(item)
    print('there are currently {} followers. {} more than last time you checked.'.format(
        len(followers), len(followers) - len(last_followers_list)))
    print('new file {} created.'.format(filename))


if __name__ == '__main__':
    check_followers()
