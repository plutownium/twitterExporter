import tweepy
import time

consumer_token = "x"
consumer_secret = "x"

access_token = "x"
access_secret = "x"

auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
auth_url = auth.get_authorization_url()
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# api.send_direct_message(331107386, "HEYyyyyyy") # works

user = api.get_user("rolypolyistaken")
print(user.followers_count)

follower_pages = tweepy.Cursor(api.followers, screen_name="rolypolyistaken").pages()

followers = []
count = 0
for page in follower_pages:
    for user in page:
        followers.append(user)
    time.sleep(65)
    count += 1
    if count == 4:
        break

for user in followers:
    print(user.location, )




# import requests
# import random
# import time
#
# now = str(time.time())
#
#
# def generate_nonce():
#     return str(random.randint(0, 1000000))
#
#
# request_headers = {"oauth_nonce": generate_nonce(),
#                    "oauth_callback": "www.google.ca",
#                    "oauth_signature_method": "HMAC-SHA1",
#                    "oauth_timestamp": now,
#                    "oauth_consumer_key": "pGFPT3qKgGNp6YPMr0wzvNVe3",
#                    "oauth_signature": "Pc%2BMLdv028fxCErFyi8KXFM%2BddU%3D",
#                    "oauth_version": "1.0"}
#
# y = requests.post("https://api.twitter.com/oauth/request_token", headers=request_headers)
#
# print(y, y.content, y.text)