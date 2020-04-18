import util # random local util function
import json

# =========================================================================
# Rowan University, Data Mining 1 Final Project
# Patrick Richeal, last modified 2020-04-18
# 
# analyze.py - Gathers statistics about the clustered posts
# =========================================================================

# open data.json file
util.log('Opening data.json...')
with open('data.json') as f:
    data = json.load(f)


num_relationship = 0
num_family = 0
num_finance = 0

num_relationship_asshole = 0
num_family_asshole = 0
num_finance_asshole = 0

for post in data['posts']:
    if post['cluster'] == 0:
        num_finance += 1
        if post['is_asshole']:
            num_finance_asshole += 1
    if post['cluster'] == 1:
        num_relationship += 1
        if post['is_asshole']:
            num_relationship_asshole += 1
    if post['cluster'] == 2:
        num_family += 1
        if post['is_asshole']:
            num_family_asshole += 1

total_posts = num_relationship + num_family + num_finance
total_asshole = num_relationship_asshole + num_family_asshole + num_finance_asshole

print("Total posts: " + str(total_posts))
print("    Relationship: " + str(num_relationship) + "(" + str(num_relationship/total_posts) + "% of all posts)")
print("    Family: " + str(num_family) + "(" + str(num_family/total_posts) + "% of all posts)")
print("    Finance: " + str(num_finance) + "(" + str(num_finance/total_posts) + "% of all posts)")
print("")
print("Total assholes: " + str(total_asshole) + "(" + str(total_asshole/total_posts) + "% of all posts)")
print("    Relationship: " + str(num_relationship_asshole) + "(" + str(num_relationship_asshole/num_relationship) + "% of all relationship posts)")
print("    Family: " + str(num_family_asshole) + "(" + str(num_family_asshole/num_family) + "% of all family posts)")
print("    Finance: " + str(num_finance_asshole) + "(" + str(num_finance_asshole/num_finance) + "% of all finance posts)")