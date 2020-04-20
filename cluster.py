from __future__ import print_function
import util # random local util function
import json
import nltk
import re
import pandas as pd
from sklearn import feature_extraction

# =========================================================================
# Rowan University, Data Mining 1 Final Project
# Patrick Richeal, last modified 2020-04-18
# 
# cluster.py - Clusters the posts from r/AmItheAsshole that were gathered
#     into data.json by get_data.py
#     
# Followed method outlined by http://brandonrose.org/clustering
# =========================================================================

# number of posts to process
PROCESS_DOCUMENTS = 9892

# open data.json file
util.log('Opening data.json...')
with open('data.json') as f:
    data = json.load(f)

# ========================================
# populate data arrays with raw data
# ========================================

posts = []
titles = []
ranks = []
i = 0
while i < PROCESS_DOCUMENTS:
    posts.append(data['posts'][i]['body'])
    titles.append(data['posts'][i]['title'])
    ranks.append(i)
    i += 1

# ========================================
# tokenize and stem the posts
# ========================================

from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

totalvocab_stemmed = []
totalvocab_tokenized = []
for i in posts:
    allwords_stemmed = tokenize_and_stem(i)
    totalvocab_stemmed.extend(allwords_stemmed)
    
    allwords_tokenized = tokenize_only(i)
    totalvocab_tokenized.extend(allwords_tokenized)

vocab_frame = pd.DataFrame({'words': totalvocab_tokenized}, index = totalvocab_stemmed)

# ========================================
# create tfidf matrix
# ========================================

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(max_df=0.2, min_df=0.1, stop_words='english', use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))
tfidf_matrix = tfidf_vectorizer.fit_transform(posts)
terms = tfidf_vectorizer.get_feature_names()
print(terms)

# ========================================
# cluster with k means using tfidf matrix
# ========================================

from sklearn.cluster import KMeans
num_clusters = 3
km = KMeans(n_clusters=num_clusters)
km.fit(tfidf_matrix)
clusters = km.labels_.tolist()
postsObj = { 'title': titles, 'rank': ranks, 'posts': posts, 'cluster': clusters }
frame = pd.DataFrame(postsObj, index = [clusters] , columns = ['rank', 'title', 'cluster'])

# ========================================
# print top terms per cluster
# ========================================

print("Top terms per cluster:")
print()
order_centroids = km.cluster_centers_.argsort()[:, ::-1]
for i in range(num_clusters):
    print("Cluster %d words:" % i, end='')
    for ind in order_centroids[i, :6]:
        print(' %s' % vocab_frame.ix[terms[ind].split(' ')].values.tolist()[0][0].encode('utf-8', 'ignore'), end=',')

# ========================================
# attach cluster number to each post in data, output data to data.json
# ========================================

i = 0
while i < PROCESS_DOCUMENTS:
    data['posts'][i]['cluster'] = frame.values[i][2]
    i += 1
with open('data.json', 'wt') as fp:
    json.dump(data, fp)
