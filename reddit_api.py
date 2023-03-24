import requests
import os

# verify file exists, if not use environment variables on heroku
if os.path.isfile("secret_words.py"):
    from secret_words import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, USERNAME, PASSWORD
else:
    REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")

# Authenticate reddit app
client_auth = requests.auth.HTTPBasicAuth(
    os.environ.get('CLIENT_ID', REDDIT_CLIENT_ID),
    os.environ.get('CLIENT_SECRET', REDDIT_CLIENT_SECRET))

post_data = {
    'grant_type': 'password',
    'username': os.environ.get('REDDIT_USERNAME', USERNAME),
    'password': os.environ.get('REDDIT_PASSWORD', PASSWORD)
}

headers = {
    'User-Agent': 'MyAPI/0.0.1'
}

# Getting Token Access ID
TOKEN_ACCESS_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
response = requests.post(TOKEN_ACCESS_ENDPOINT,
                            auth=client_auth, data=post_data, headers=headers)

if response.status_code == 200:
    token_id = response.json()['access_token']

# Accessing reddit's REST API
OAUTH_ENDPOINT = 'https://oauth.reddit.com'

params_get = {
    'limit': 10
}

params_get_jokes = {
    'limit': 5
}

headers_get = {
    'User-Agent': 'MyAPI/0.0.1',
    'Authorization': 'Bearer ' + token_id
}


# gets api data for top posts and jokes
res_top = requests.get(OAUTH_ENDPOINT + '/r/TodayILearned/top', headers=headers_get, params=params_get)

res_joke = requests.get(OAUTH_ENDPOINT + '/r/Jokes/top', headers=headers_get, params=params_get_jokes)


def get_comments(post_url):
    '''Get the top comment from a post.'''

    result = []

    params = {
        "sort": "top",
        "limit": 1,
    }

    res = requests.get(OAUTH_ENDPOINT + post_url, headers=headers_get, params=params)

    for post in res.json():
        result.append(post['data']['children'][0]['data'].get('body'))

    return result[1]