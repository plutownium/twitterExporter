import tweepy
from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import os

from google.cloud import firestore

# this app extracts any set of msgs in the db and send them

credential_path = "H:\Downloads Folder\\andy-twitter-engagement-41de798f1f5c.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


# class Message:
#     def __init__(self, sender_id, recipient_id, message):
#         self.sender_id = sender_id
#         self.recipient_id = recipient_id
#         self.message = message


app = Flask(__name__)
CORS(app)


@app.route("/ready/<consumer_token>/<consumer_secret>/<access_token>/<access_secret>/<username>/", methods=["GET"])
def start_dms(consumer_token, consumer_secret, access_token, access_secret, username):
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth_url = auth.get_authorization_url()
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    db = firestore.Client()

    # ### start getting batches of 950 DMs from the firestore DB and sending them

    # TODO: ANDY i don't understand how "send 950 then pause" is different from "send 1 then pause" in terms of VM usage
    doc_ref = db.collection(u'users').document(username).collection(u'messages')

    while True:  # loop as many times as it takes to get ALL the msg documents from the user's collection
        # get 950 of the highest priority DMs
        query = doc_ref.order_by(u'priority', direction=firestore.Query.DESCENDING).limit(950)
        results = query.stream()

        # for each result, package it into a tweepy "send DM" api call, pause for a sec, repeat
        for result in results:
            print(result)  # check what the "result" object contains
            break
            api.send_direct_message(result.recipient, result.message)  # i think it will be like this (but test still)
            # https://developer.twitter.com/en/docs/basics/rate-limits says we can do 1000 DMs / 24 hrs

        # delete the finished batch of DMs so the db isn't clogged with old data
        # (and so line 42 retrieves a new batch of message docs)
        for result in results:
            # TODO: validate that "results" is a batch of firestore docs
            result.delete()  # https://firebase.google.com/docs/firestore/manage-data/delete-data

        # if the query received less than 950 docs, clearly we are in the last batch of DMs; don't need to loop again
        if len(query) < 950:
            break

        time.sleep(24*61*60)  # sleep for just over 24 hours to avoid the "POST limit window"


if __name__ == '__main__':
    app.run()
