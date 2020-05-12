import os
import re

import praw


KEYWORD = 'Luigi'
SUBREDDIT = 'GameSale'

MESSAGE_BODY_SUBMISSION_ID_KEY = 'Post ID: '

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')


# specifically looking for the selling section
def get_relevant_part_of_title(title):
    relevant_title = re.search(r'.*?\[H\](.*?)\[W\]', title)

    if relevant_title:
        return relevant_title.group(1)
    else:
        return None


def search_keyword_in_title(relevant_title, keyword):
    return keyword.lower() in relevant_title.lower()


def send_private_message(reddit, submission):
    subject = 'GAMESALEBOT: ' + submission.title
    body = '''Link: <{url}>\n\n{post_key}{submission_id}
    '''.format(
        url=submission.url,
        post_key=MESSAGE_BODY_SUBMISSION_ID_KEY,
        submission_id=submission.id)

    reddit.redditor('mrbowow').message(subject, body)


def get_seen_submission_ids(reddit):
    seen = []

    for message in reddit.inbox.sent(limit=50):
        if 'GAMESALEBOT' in message.subject:
            seen.append(get_submission_id_from_private_message(message.body))

    return seen


def get_submission_id_from_private_message(body):
    return re.search(r'.*?Post ID: (.*)', body).group(1)


def lambda_handler(event, context):
    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         user_agent="my user agent",
                         username=USERNAME,
                         password=PASSWORD)

    seen_submission_ids = get_seen_submission_ids(reddit)

    for submission in reddit.subreddit(SUBREDDIT).new(limit=20):
        relevant_title = get_relevant_part_of_title(submission.title)

        if relevant_title \
                and submission.id not in seen_submission_ids \
                and search_keyword_in_title(relevant_title, KEYWORD):
            send_private_message(reddit, submission)


if __name__ == '__main__':
    lambda_handler(None, None)