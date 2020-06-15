import tweepy
import time
import datetime
import atexit
import io
import timeit

APP_VERSION = "0.1"
TOTAL_ERRORS = 0
API_ACCESS_DELAY = 65  # recommend keeping this at 61 or greater (or else the API rate limit will be hit)
MESSAGE_DELAY = 91  # recommend keeping this at 90 or greater (or else the daily DM limit will be hit)

MESSAGED_USERS = []


def check_username(username):
    print("Is your username correct?")
    print("You entered: ", username)
    response = input("enter y/n: ")
    if response == "y":
        return True
    elif response == "n":
        return False
    else:
        answer = check_username(username)
        return answer


def check_message(msg):
    print("Is your message correct? Please proof read, it's going to your *whole list*!")
    print("You entered: ", msg)
    response = input("enter y/n: ")
    if response == "y":
        return True
    elif response == "n":
        return False
    else:
        answer = check_message(msg)
        return answer


# if error, log the error into a .txt file so user can report it to developer
def report_error(error):
    global TOTAL_ERRORS
    TOTAL_ERRORS += 1
    date = datetime.date.today()
    filename = "error_report" + str(date) + "error" + str(TOTAL_ERRORS) + ".txt"
    f = open(filename, "w")
    f.write("Tell Roland Mackintosh about this error using rolandmackintosh@outlook.com\n\nError:\n\n")
    f.write(str(error))
    f.write("\n\n")
    f.write(str(APP_VERSION))
    f.close()

# TODO: Handle case where program exits midway thru messaging users...
# TODO: Can the program add messaged users to a list of "already messaged users"?
# TODO: And then detect that database's contents the next time the process is run?
# TODO: Perhaps this is a job for Firestore? "Avoid messaging users twice"


def startup_handler():
    # runs on startup, opens the day's database file if there is one, parses contents

    # open today's database file

    date = datetime.date.today()
    filename = "messaged_users_" + str(date) + ".txt"
    f = open(filename, "w")

    # parse contents
    try:
        contents = f.read()
    except io.UnsupportedOperation as cant_read:
        report_error(cant_read)
        return False

    contents = contents.splitlines()

    # get the ids of people who were already messaged
    just_the_ids = []
    for id_and_screen_name in contents:
        # get the id and convert it to int (int is used later on line 163)
        user_id_as_int = int(id_and_screen_name.split(" ")[0])
        just_the_ids.push(user_id_as_int)

    f.close()

    if len(just_the_ids) > 0:
        return just_the_ids
    else:
        return False


def exit_handler():
    date = datetime.date.today()
    filename = "messaged_users_" + str(date) + ".txt"
    f = open(filename, "w")

    f.write("Processs started on: " + str(date))
    f.write("\n\n")
    with_message = "With message: " + message
    f.write(with_message)
    f.write("\n\n")
    f.write("List of messaged users:\n\n")

    for messaged_user in MESSAGED_USERS:
        user_id_and_screen_name = str(messaged_user.id_str) + " " + str(messaged_user.screen_name)
        f.write(user_id_and_screen_name)
        f.write("\n")

    f.close()


atexit.register(exit_handler)

start = timeit.default_timer()
start_date = datetime.date.today().strftime("%b-%d-%Y")

consumer_token = input("Enter your consumer token: ")
consumer_secret = input("Enter your consumer secret: ")

access_token = input("Enter your access token: ")
access_secret = input("Enter your consumer secret: ")

username = input("Enter your account name: ")
message = input("Enter a message to send: ")


name_validation = check_username(username)
msg_validation = check_message(message)

if name_validation and msg_validation:
    pass
else:
    # TODO: do something better than forcing the user to restart the program because of a typo
    print("Restarting program to try the inputs again...")
    time.sleep(3)
    exit()


auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
auth_url = auth.get_authorization_url()
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# On startup, look for any database file created
already_messaged_users = startup_handler()

# collect list of followers
follower_pages = tweepy.Cursor(api.followers, screen_name=username).pages()

# Tell the site how long it's expected to take
account_followers = api.get_user(username).followers_count
results_per_page = 20
time_to_get_users = account_followers / results_per_page * API_ACCESS_DELAY / 60  # in minutes
time_to_message_users = account_followers * MESSAGE_DELAY / 60  # in minutes
expected_duration = int((time_to_get_users + time_to_message_users) / 60)  # in hours
expected_days = int(expected_duration / 24)  # int() turns float to integer (removes decimals)


print("Based on your {0} twitter followers, you can expect this to take {1} hours or {2} days."
      .format(account_followers, expected_duration, expected_days))

followers = []
followers_by_follower_count = []
total_sent_msgs = 0

# each loop clearly sends a request, as there is a delay between loops
# to observe, try looping "for page in follower_pages: print(page)" and observe that it has a delay
for page in follower_pages:
    for user in page:
        followers.append(user)

    # # TODO: comment out the break for the live version (for testing purposes, it is useful to break here)
    # break  # prevents app from getting all results, instead limits it to only 1 page (20 users)
    time.sleep(API_ACCESS_DELAY)  # avoid API Rate Limit

# organize followers list with biggest accounts first
followers_by_follower_count = sorted(followers, key=lambda x: x.followers_count)

# send message to 950 followers (what to do for ppl with closed DMs?) over a 24 hr period.
# NOTE: 24 hrs * 60 min / hr = 1440 mins, so 1440 mins / 950 msgs = 1.52 minutes between messages (91 seconds)
total_daily_loops = 0

for index, follower in enumerate(followers_by_follower_count, start=1):
    # check if follower was already messaged
    if already_messaged_users:  # TODO: somehow test this without messaging my entire followers list... impossible?
        # "is follower in already_messaged_users? if so, skip this loop"
        if int(follower.id_str) in already_messaged_users:
            continue

    # Message follower and then add him to list of users who have been messaged
    try:
        # print("Sending direct msg to {0} who is index {1}".format(follower.screen_name, index))
        # TODO: disable next line if developing so you don't msg all your friends
        api.send_direct_message(follower.id_str, message)
        MESSAGED_USERS.append(follower)
        time.sleep(MESSAGE_DELAY)  # avoid exceeding Twitter's Daily DM Limit of 1000
        total_daily_loops += 1
        total_sent_msgs += 1
    except Exception as e:
        error_msg = "for user " + str(follower.screen_name) + " cannot msg user because: " + str(e)
        error_msg = "cannot msg user because: "
        total_daily_loops += 1
        report_error(error_msg)

    # Inform the user how much time is left on the process and how many users have been messaged.
    # NOTE: 120 mins / 1.52 mins between msgs = 79 users per 120 mins
    # do this approx every 120 min
    if index % 79 == 0:
        now = timeit.default_timer()
        run_time = now - start
        remaining_users = len(followers) - index
        time_to_go = str(MESSAGE_DELAY*remaining_users)
        print("You have messaged {0} users out of {1}. Elapsed time: {2}. Time to go: {3}"
              .format(index, len(followers), run_time, time_to_go))

    # every 950 messages, pause for an hour (extra effort to avoid getting blacklisted)
    if total_daily_loops > 949:
        time.sleep(60*60)  # pause for an hour
        total_daily_loops = 0

    # restart loop sending message to 950 followers

# generate a little .txt file at the end of the process
# include a note to the user to re-run the program in a month or something to remind followers that the user
# has changed platforms
end_date = datetime.date.today().strftime("%b-%d-%Y")
end_message = "Your message bot started its work on {0} and finished on {1}. You sent {2} messages."\
    .format(start_date, end_date, total_sent_msgs)
success_msg_filename = "success_msg_" + str(end_date) + ".txt"

end_file = open(success_msg_filename, "w")
end_file.write(end_message)
end_file.write("\n\nConsider re-running the application in a month's time with a follow-up message.")
end_file.close()

exit()

