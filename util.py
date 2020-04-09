import datetime

# ==================================================================
# Rowan University, Data Mining 1 Final Project
# Patrick Richeal, last modified 2020-04-09
# 
# util.py - Various utility functions
# ==================================================================

def log(text):
    now = datetime.datetime.now()
    print('[' + now.strftime("%I:%M:%S") + '] ' + text)