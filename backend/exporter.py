import tweepy
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# declaring global variables
API_ACCESS_DELAY = 65  # recommend keeping this at 61 or greater (or else the API rate limit will be hit)
MESSAGE_DELAY = 91  # recommend keeping this at 90 or greater (or else the daily DM limit will be hit)

# TODO: request 1, initiates "msg all followers" even if it takes 200 days
# TODO: request 2, returns "how long it will take" so the site can display it to the user

# TODO: return a code to the user that (somehow) cancels the process when sent to the server.

# TODO: rank twitter followers by geolocation. For followers with < 5k followers, prioritize North Americans
# TODO: rank twitter followers by account activity. "How many tweets are they writing per week?" More is better.
# how would I do that... how long would it take per account... hmm...


def rank_by_activity_and_language(input_list, activity=True, lang=False, crypto=False):
    # ### Ranks followers by activity, language,
    # and "mentions crypto bio".
    # Also (perhaps most importantly) tries to detect if user location is in North America.

    print("hi")
    return True


def detect_keywords(followers, keyword_list):
    # ### user supplies keyword list. function checks each user's bio, screen name, whatever, for the keywords.
    return None


@app.route("/send_message/ctoken/<consumer_token>/csecret/<consumer_secret>/atoken/<access_token>/asecret/<access_secret>/username/<username>/msg/<message>/", methods=["GET", "POST"])
def message_all_followers(consumer_token, consumer_secret, access_token, access_secret, username, message):
    # ### does what it says

    # authenticate using supplied info
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth_url = auth.get_authorization_url()
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # retrieve user's followers

    follower_pages = tweepy.Cursor(api.followers, screen_name=username).pages()
    followers = []
    count = 0
    for page in follower_pages:
        count += 1
        if count == 14:
            time.sleep(60*16)  # avoid rate limit... 60 sec per min times 16 min
            count = 0  # reset count
        try:
            print("page:", page)
            for user in page:
                followers.append(user)
                # print("HI:", user.id_str, user.screen_name, user.followers_count, user.location)  # prints
                print("HI:", user.id_str, user.location)  # prints
        # what happens when we hit 'rate limit exceeded'
        except Exception as e:
            print(e)  # TODO: test a few times and see what errors come up.
            time.sleep(60*16)  # 60 sec * 16 minutes, one minute longer than needed (just in case)

    # after assembling a list of followers, order them by .followers_count
    followers_ranked = sorted(followers, key=lambda x: x.followers_count)

    # enable this function to rank followers below a threshold of followers by activity
    # followers_ranked = rank_by_activity_and_language(followers_ranked,
    #                                                      activity=True,
    #                                                      lang="En",
    #                                                      crypto=True)

    # TODO: "for follower.followers_count < 2000, move US based followers to the top and sort by followers_count"

    # NOTE: Twitter DMs are limited to 1,000 in a day.
    # For safety, let's limit ourselves to 800 per day. Don't want to anger Twitter.
    # Math: 24 hrs * 60 minutes = 1440 minutes in a day.
    # Therefore, approximately one DM every 2 minutes is fine. (720 msgs / day)
    # (To hit 999 messages in a day, change "message_delay" to 1.44)
    message_delay = 1.8

    for follower in followers_ranked:
        print("sending msg to:", follower.id_str)
        api.send_direct_message(follower.id_str, message)
        time.sleep(60 * message_delay)

    return "Done!"  # todo: what to return?


@app.route("/get_eta_and_followers/ctoken/<consumer_token>/csecret/<consumer_secret>/atoken/<access_token>/asecret/<access_secret>/username/<username>/", methods=["GET"])
def get_eta_and_followers(consumer_token, consumer_secret, access_token, access_secret, username):
    # ### route tells the client how long the process will take

    # authenticate using supplied info
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth_url = auth.get_authorization_url()
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    account_followers = api.get_user(username).followers_count
    results_per_page = 20
    time_to_get_users = account_followers / results_per_page * API_ACCESS_DELAY / 60  # in minutes
    time_to_message_users = account_followers * MESSAGE_DELAY / 60  # in minutes
    total_seconds = time_to_get_users + time_to_message_users

    expected_hours = int(total_seconds / 60)  # in hours
    expected_days = int(expected_hours / 24)  # int() turns float to integer (removes decimals)

    return jsonify(account_followers=account_followers,
                   duration_in_hours=expected_hours,
                   duration_in_days=expected_days)


# FIXME: what to do if multiple users are using this server at the same time? does the api validation conflict?
#  will that use case ever even occur?

if __name__ == '__main__':
    app.run()
