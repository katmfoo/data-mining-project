import util # random local util functions
import configparser
import praw # reddit sdk
from psaw import PushshiftAPI # reddit sdk wrapper
import re
import datetime
import json
import html

# =========================================================================
# Rowan University, Data Mining 1 Final Project
# Patrick Richeal, last modified 2020-04-09
# 
# get_data.py - Scrapes the r/AmItheAsshole subreddit to gather posts and
#     analyzes the comments to find the following abbreviations
#
#       YTA - you're the asshole
#       NTA - not the asshole
#       ESH - everyone sucks here
#       NAH - no assholes here
#
#     Saves the title/body of the post along with the amount of each of
#     the above mentions to a json file
# =========================================================================

# get config data
util.log('Reading config data...')
config = configparser.ConfigParser()
config.read('config.ini')

# setup list of symbols to search for
symbols = ['yta', 'nta', 'esh', 'nah']

# function to find any stock symbol in given string
def get_symbol_matches(text):
    matches = {
        'yta': 0,
        'nta': 0,
        'esh': 0,
        'nah': 0
    }
    for symbol in symbols:
        result = re.search(symbol, text)
        if result != None:
            matches[symbol] += 1
    return matches

# regex for alpha and spaces only
alpha_regex = re.compile('[^a-zA-Z ]')

# initialize reddit sdk object
util.log('Initializing reddit sdks...')
reddit = praw.Reddit(
    client_id=config['reddit']['client_id'],
    client_secret=config['reddit']['client_secret'],
    user_agent=config['reddit']['user_agent']
)
api = PushshiftAPI(reddit)

# setup submission generator to loop over reddit posts on subreddit over given date range
util.log('Setting up submission generator...')
start_epoch=int(datetime.datetime(2019, 11, 1).timestamp())
end_epoch=int(datetime.datetime(2019, 11, 30).timestamp())
submission_generator = api.search_submissions(subreddit = 'AmItheAsshole', after = start_epoch, before = end_epoch)

def clean_text(text):
    # lower case all chars
    text = text.lower()

    # html unescape entity codes
    text = html.unescape(text)

    # remove any special chars
    text = text.replace('\n\n', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\\*', '')
    text = text.replace('\\~', '')
    text = text.replace('\\', '')
    text = text.replace('/', ' ')
    text = text.replace('*', '')

    # remove any escaped double quotes
    text = text.replace('\"', '')

    # remove any unicode sequences
    text = text.encode('ascii', 'ignore').decode("utf-8")

    return text

# setup dictionary object to store posts
data = {
    'num_posts': 0,
    'posts': []
}

# loop over submissions
util.log('Gathering posts and counting abbreviations in comments...')
for submission in submission_generator:

    # format title and body to alpha only lower case
    title = clean_text(submission.title)
    body = clean_text(submission.selftext)

    # ignore deleted or removed posts
    if body in ['[deleted]', '[removed]']:
        continue

    # setup object to hold number of symbol mentions in comments
    comment_mentions = {
        'yta': 0,
        'nta': 0,
        'esh': 0,
        'nah': 0
    }

    comments = []
    # look through comments for abbreviations
    for comment in submission.comments:
        if hasattr(comment, 'body'):
            comment_body = clean_text(comment.body)[0:10]
            matches = get_symbol_matches(comment_body)
            comment_mentions['yta'] += matches['yta']
            comment_mentions['nta'] += matches['nta']
            comment_mentions['esh'] += matches['esh']
            comment_mentions['nah'] += matches['nah']
            comments.append(comment_body)
    
    is_asshole = False
    if (comment_mentions['yta'] + comment_mentions['esh']) > (comment_mentions['nta'] + comment_mentions['nah']):
        is_asshole = True

    # add post to beginning of list
    data['posts'].insert(0, {
        'title': title,
        'datetime': datetime.datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
        'num_comments': len(submission.comments),
        'comment_mentions': comment_mentions,
        'is_asshole': is_asshole,
        'comments': comments,
        'body': body
    })

    # update post count
    data['num_posts'] += 1

    with open('data.json', 'wt') as fp:
        json.dump(data, fp)

print('Done!')