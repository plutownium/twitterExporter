import tweepy
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import requests
import datetime

from google.cloud import firestore

import os

# Generate a list of DMs the service wants sent
# insert the list of DMs into firestore

# https://stackoverflow.com/questions/54947486/python-firestore-issue-with-authentication
credential_path = "H:\Downloads Folder\\andy-twitter-engagement-41de798f1f5c.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


class Message:
    def __init__(self, sender_id, recipient_id, message):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message = message


app = Flask(__name__)
CORS(app)

@app.route("/input/<consumer_token>/<consumer_secret>/<access_token>/<access_secret>/<username>/<message>/",
           methods=["GET"])
def generate_and_store_dms(consumer_token, consumer_secret, access_token, access_secret, username, message):
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth_url = auth.get_authorization_url()
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # retrieve user's followers

    follower_pages = tweepy.Cursor(api.followers, screen_name=username).pages()
    followers = []
    count = 0
    for page in follower_pages:
        print("Going thru a page")
        count += 1
        if count == 14:
            print("Sleeping for 16*60")
            break
            time.sleep(60 * 16)  # avoid rate limit... 60 sec per min times 16 min
            count = 0  # reset count
        try:
            print("page:", page)
            for user in page:
                followers.append(user)
                # print("HI:", user.id_str, user.screen_name, user.followers_count, user.location)  # prints
                # print("HI:", user.id_str, user.location)  # prints
        # what happens when we hit 'rate limit exceeded'
        except Exception as e:
            print(e)  # TODO: test a few times and see what errors come up.
            time.sleep(60 * 16)  # 60 sec * 16 minutes, one minute longer than needed (just in case)

    # after assembling a list of followers, order them by .followers_count
    followers_ranked = sorted(followers, key=lambda x: x.followers_count)

    # create a list of items to post into the firestore db
    messages = []

    script_user = api.get_user(screen_name=username)

    print("number of followers retrieved: {0}".format(len(followers_ranked)))
    for follower in followers_ranked:  # andy I don't understand how to turn
        # msg_to_send = Message(script_user.id, follower.id, message)
        msg_to_send = {"sender": script_user.id,
                       "recipient": follower.id,
                       "message": message,
                       "priority": follower.followers_count,
                       "time-posted": datetime.datetime.now()}
        messages.append(msg_to_send)

    # now upload all these messages-in-potential to the firestore
    db = firestore.Client()

    # print("attempting to push {0} items to the db".format(len(messages)))
    # post the entire list of items all at once
    for msg in messages:
        db.collection(u'users').document(username).collection(u'messages').add(msg)
    # print("wow it worked!")

    # send msg to the micro-service responsible for sending msgs telling it to start. also fwd credentials
    app_ip_and_port = ""
    url_path = "/ready/" + consumer_token + "/" + consumer_secret + "/" \
               + access_token + "/" + access_secret + "/" + username
    rdy = requests.get(app_ip_and_port + url_path)

    return "done!"


if __name__ == '__main__':
    app.run()
