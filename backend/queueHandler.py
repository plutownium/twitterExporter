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

    # ### start getting batches of 950 DMs from the firestore DB and sending them

    db = firestore.Client()

    # NOTE: ANDY i don't understand how "send 950 then pause" is different from "send 1 then pause" in terms of VM usage
    doc_ref = db.collection(u'users').document(username)
    doc = doc_ref.get()

    msg_content = ""

    messages_to_send = []
    if doc.exists:
        data = doc.to_dict()
        msg_content = data["message"]
        for follower in data["recipients"]:
            messages_to_send.append(follower)

    messages_by_priority = sorted(messages_to_send, key=lambda x: x["priority"], reverse=True)

    total_msgs_sent_today = 0
    for msg in messages_by_priority:
        api.send_direct_message(msg["recipient"], msg_content)
        total_msgs_sent_today += 1
        time.sleep(1)  # seems reasonable to insert a 1 second pause between DMs to avoid rate limits or something

        break  # disable this in the live version. in the demo, it prevents the script from msging ALL your followers to test the code

        if total_msgs_sent_today > 949:
            time.sleep(24 * 61 * 60)
            total_msgs_sent_today = 0


if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=8080)
    app.run()
