import tweepy
import time
import datetime
import timeit

APP_VERSION = "0.2"
TOTAL_ERRORS = 0
API_ACCESS_DELAY = 65  # recommend keeping this at 61 or greater (or else the API rate limit will be hit)
MESSAGE_DELAY = 91  # recommend keeping this at 90 or greater (or else the daily DM limit will be hit)

# TODO: Validate that tokens, secrets, and username have NO COMMAS in them! A comma will BREAK the database file!


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
        # FIXME: does returning False make sense? What about this "answer = check_message(msg)" thing? whats that about?
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


# TODO: Make the program use ONE .txt file as its database --
#  TODO: and add a follower's id_str to the .txt db after every msg is sent.

def get_already_messaged_users():
    """ runs on startup, opens the database file if there is one, parses contents
    :return: a list, just_the_ids, of the followers who have already been messaged, False if no db exists
    """
    # TODO: prevent func from acting on the first 2 lines of db file. these contain tokens, secrets, username, msg
    # parse contents
    try:
        filename = "twitter_messager_bot_database.txt"
        f = open(filename, "r")
        contents = f.read()
        contents = contents.splitlines()
        f.close()

        # get the ids of people who have not yet been messaged
        just_the_ids = []
        for id_and_screen_name in contents[2:]:
            # get the id and convert it to int (int is used later on line 163)
            user_id_as_int = int(id_and_screen_name.split(" ")[0])
            just_the_ids.append(user_id_as_int)

        if len(just_the_ids) > 0:
            return just_the_ids
        else:  # NOTE: this else should seemingly never happen?
            return False
    except FileNotFoundError:
        report_error("Error 9000: Database file not found!")
        return False


def add_follower_to_database(user_id, user_screen_name):
    """runs every time the api sends a direct message. logs the fact that the follower was msg'd
    so the user can close the program and pick up where he left off.
    :return: True if successful, False if failure
    """

    new_entry = str(user_id) + " " + str(user_screen_name) + "\n"

    try:
        filename = "twitter_messager_bot_database.txt"
        f = open(filename, "a")
        f.write(new_entry)
        f.close()
        return True
    except FileNotFoundError:
        report_error("Error 801: Could not add follower to database!")
        return False

# ### ### ###
# ### ### ###
# ### ### ###
# "Start"
# ### ### ###
# ### ### ###
# ### ### ###


start = timeit.default_timer()  # record when the process began
start_date = datetime.date.today().strftime("%b-%d-%Y")

# On startup, look for any database file created
already_messaged_users = get_already_messaged_users()  # will either be a list of user id_strs or False

if already_messaged_users:  # if there was a database file, use the key and tokens they supplied
    # retrieve the data from the .txt db file
    f = open("twitter_messager_bot_database.txt", "r")
    tokens_and_secrets_and_username = f.readline().split(",")

    consumer_token = tokens_and_secrets_and_username[0]
    consumer_secret = tokens_and_secrets_and_username[1]

    access_token = tokens_and_secrets_and_username[2]
    access_secret = tokens_and_secrets_and_username[3]

    username = tokens_and_secrets_and_username[4][0:-1]  # 0:-2 to strip out the newline char
    message = f.readline()[0:-1]  # 0:-2 to strip out the newline char
    f.close()

else:  # if there was no database file, get keys and tokens from the user for the first time
    consumer_token = input("Enter your consumer token: ")  # TODO: if comma detected, try again
    consumer_secret = input("Enter your consumer secret: ")

    access_token = input("Enter your access token: ")
    access_secret = input("Enter your consumer secret: ")

    username = input("Enter your account name: ")
    message = input("Enter a message to send: ")

    name_validation = check_username(username)  # FIXME: if user doesn't enter "y", re-do name input (same for msg)
    msg_validation = check_message(message)

    if name_validation and msg_validation:
        # write all the info into a database file
        f = open("twitter_messager_bot_database.txt", "w")
        base_data = consumer_token + "," + consumer_secret + "," + access_token + "," + access_secret + "," + username
        f.write(base_data)
        f.write("\n")
        f.write(message)
        f.write("\n")
        f.close()
        pass
    else:
        # TODO: do something better than forcing the user to restart the program because of a typo
        print("Restarting program to try the inputs again...")
        time.sleep(3)
        exit()

try:
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
    auth_url = auth.get_authorization_url()
    auth.set_access_token(access_token, access_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
except Exception as some_error:
    report_error(some_error)
    print("Something went wrong! Is your API key and access token/secret being entered correctly?")
    print("Program exiting in 5...")
    time.sleep(5)
    exit()

# TODO: save the api keys and tokens, account name, and message content into the database file.
# TODO: if database file exists, run using the database contents; if it doesn't exist, prompt user to fill in info

# Tell the site how long it's expected to take
if already_messaged_users:
    print("USERNAME:", username)
    print("MSG:", message)
    account_followers = api.get_user(username).followers_count
    remaining_followers = account_followers - len(already_messaged_users)

    results_per_page = 20
    time_to_get_users = account_followers / results_per_page * API_ACCESS_DELAY / 60  # in minutes
    time_to_message_users = remaining_followers * MESSAGE_DELAY / 60  # minutes - NOTE "remaining_followers" here
    expected_duration = int(time_to_message_users / 60)  # in hours
    expected_days = int(expected_duration / 24)  # int() turns float to integer (removes decimals)
    print("Based on {0} remaining followers to be messaged, you can expect this to take {1} hours or {2} days."
          .format(remaining_followers, expected_duration, expected_days))
else:
    account_followers = api.get_user(username).followers_count

    results_per_page = 20
    time_to_get_users = account_followers / results_per_page * API_ACCESS_DELAY / 60  # in minutes
    time_to_message_users = account_followers * MESSAGE_DELAY / 60  # in minutes - NOTE "account_followers" here
    expected_duration = int((time_to_get_users + time_to_message_users) / 60)  # in hours
    expected_days = int(expected_duration / 24)  # int() turns float to integer (removes decimals)
    print("Based on your {0} twitter followers, you can expect this to take {1} hours or {2} days."
          .format(account_followers, expected_duration, expected_days))

# collect list of followers
print("Collecting list of followers... will take approx {0} minutes before the DMs start going."
      .format(int(API_ACCESS_DELAY * api.get_user(username).followers_count / 20 / 60)))
follower_pages = tweepy.Cursor(api.followers, screen_name=username).pages()

followers = []
followers_by_follower_count = []
total_sent_msgs = 0

# each loop clearly sends a request, as there is a delay between loops
# to observe, try looping "for page in follower_pages: print(page)" and observe that it has a delay
# pagecounter = 0
for page in follower_pages:
    for user in page:
        followers.append(user)

    # # TODO: comment out the break for the live version (for testing purposes, it is useful to break here)
    # break  # prevents app from getting all results, instead limits it to only 1 page (20 users)
    print("Sleeping for {0}. currently at {1} users".format(API_ACCESS_DELAY, len(followers)))
    time.sleep(API_ACCESS_DELAY)  # avoid API Rate Limit
    # pagecounter += 1
    # if pagecounter == 6:
    #     break


# organize followers list with biggest accounts first
followers_by_follower_count = sorted(followers, key=lambda x: x.followers_count)

# send message to 950 followers (what to do for ppl with closed DMs?) over a 24 hr period.
# NOTE: 24 hrs * 60 min / hr = 1440 mins, so 1440 mins / 950 msgs = 1.52 minutes between messages (91 seconds)
total_daily_loops = 0

# ###
# ### "message followers" loop
# ###
for index, follower in enumerate(followers_by_follower_count, start=1):
    # check if follower was already messaged
    if already_messaged_users:  # TODO: somehow test this without messaging my entire followers list... impossible?
        # "is follower in already_messaged_users? if so, skip this loop"
        if int(follower.id_str) in already_messaged_users:
            print("Skipping a follower who was messaged last time:", follower.screen_name)
            continue

    # Message follower and then add him to list of users who have been messaged
    try:
        print("Sending direct msg to {0} who is follower {1} of {2}".format(follower.screen_name, index,
                                                                         len(followers_by_follower_count)))
        # TODO: disable next line if developing so you don't msg all your friends
        api.send_direct_message(follower.id_str, message)
        add_follower_to_database(follower.id_str, follower.screen_name)
        time.sleep(MESSAGE_DELAY)  # avoid exceeding Twitter's Daily DM Limit of 1000
        # time.sleep(3)  # TODO: change to "MESSAGE_DELAY" if in production
        total_daily_loops += 1
        total_sent_msgs += 1
    except Exception as e:
        error_msg = "for user " + str(follower.screen_name) + " cannot msg user because: " + str(e)
        report_error(error_msg)
        total_daily_loops += 1

    # Inform the user how much time is left on the process and how many users have been messaged.
    # NOTE: 120 mins / 1.52 mins between msgs = 79 users per 120 mins
    # so, do this approx every 120 min
    if index % 79 == 0:
        now = timeit.default_timer()
        run_time = now - start
        remaining_users = len(followers) - index
        time_to_go = str(MESSAGE_DELAY * remaining_users / 60)
        print("You have messaged {0} users out of {1}. Elapsed time: {2}. Time to go: {3} minutes"
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

# TODO: mk db file autodelete when its number of names is equal to the user's # of twitter followers ... or something?
# TODO: maybe something like,
#  print("The number of names in the database file is now equal to your number of twitter followers.")
#  print("Delete the database file to start again.")

# def exit_handler():
#     date = datetime.date.today()
#     filename = "messaged_users_" + str(date) + ".txt"
#     f = open(filename, "w")
#
#     f.write("Processs started on: " + str(date))
#     f.write("\n\n")
#     with_message = "With message: " + message
#     f.write(with_message)
#     f.write("\n\n")
#     f.write("List of messaged users:\n\n")
#
#     for messaged_user in MESSAGED_USERS:
#         user_id_and_screen_name = str(messaged_user.id_str) + " " + str(messaged_user.screen_name)
#         f.write(user_id_and_screen_name)
#         f.write("\n")
#
#     f.close()
#
#
# atexit.register(exit_handler)
