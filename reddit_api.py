from secrets import CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD
import requests

# Authenticate reddit app
client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

post_data = {
    'grant_type': 'password',
    'username': USERNAME,
    'password': PASSWORD
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

res_top = requests.get(OAUTH_ENDPOINT + '/r/TodayILearned/top', headers=headers_get, params=params_get)

# test to see if it returns joke data
res_joke = requests.get(OAUTH_ENDPOINT + '/r/Jokes/top', headers=headers_get, params=params_get_jokes)


# for post in res_top.json()['data']['children']:
#     print(post['data']['title'])
#     print(post['data']['url'])
#     print(post['data']['permalink'])


# def get_data(data):
#     '''Retrieve JSON type.'''
#     post_info = []

#     for post in data.json()['data']['children']:
#         # print(post['data']['title'])
#         # print(post['data']['url'])

#         post_info.append({ 
#             'title': post['data']['title'],
#             'url': post['data']['url']
#         })
    
#     return post_info


# print(get_data(res_top)[0])



# ===========================================

# look @ video - 11:00

"""
data that is needed:
    title
    url
    comments  - (top 3)
    selftext from jokes only
"""


# do for loop to extract data from specific keys
# maybe make a function that handles that?