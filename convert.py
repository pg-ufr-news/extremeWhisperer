import os
import sys
import math

import pandas as pd

from pathlib import Path
import os.path
import glob

import aiohttp
import asyncio
import requests
from urllib.parse import urlparse
import json
import time
import smtplib
import random
import hashlib
import glob
from difflib import SequenceMatcher


import datetime
#from datetime import timezone
from dateutil import parser
from datetime import date, timedelta, datetime, timezone

DATA_PATH = Path.cwd()

topicColors = {'Thunderstorm':'#53785a', 'Flood':'#030ba1', 'Storm':'#b3b2b1', 'Storm Surge':'#834fa1', 'Flash Flood':'#02b5b8',
               'Tsunami':'#690191', 'Drought':'#edc291', 'Earthquake':'#870007', 'Landslide':'#572c03', 'Cold Wave':'#a7e9fa', 'Heat Wave':'#c40202',
               'Tropical Cyclone':'#4f4f4f', 'Volcano':'#b83202', 'Snow Avalanche':'#deddd5', 'unknown':'#d60d2b'  
               }

topicsFields = ["module", "topic", "feed", "term", "created", "added", "language", "ratio", "location", "latitude", "longitude"]
keywordsFields = ["keyword","language","topic","topicColor","keywordColor","limitPages","ratioNew"]
termsFields = ["module", "topic", "color", "feed", "term", "created", "country", "ratio", "counter", "pages", "language"]
topicsDict = {}
if(os.path.isfile(DATA_PATH / 'topics.csv')):
  topicsDF = pd.read_csv(DATA_PATH / 'topics.csv', delimiter=',', index_col='index')
  keywordsDF = topicsDF
  ## keywordsDF = keywordsDF.rename(columns={"term": "keyword"}, errors="raise") 
  ## keywordsDF = keywordsDF.rename(columns={"ratio": "ratioNew"}, errors="raise") 
  keywordsDF['color'] = keywordsDF['topic'].apply(
    lambda x: topicColors[x] if (x in topicColors) else topicColors['unknown'] 
        
  )
  keywordsDF['ratio'] = 0.7*keywordsDF['ratio']
  keywordsDF['pages'] = 2
  keywordsDF['counter'] = 0
  keywordsDF['country'] = None
  ## topicsDF['feed'] = 'unknown' # DONE
  topicsDict = topicsDF.to_dict('index') 
  keywordsDF = keywordsDF.sort_values(by=['ratio'], ascending=False)

  print('88888888888888888888888')
  print(keywordsDF)

  keywordsDF.to_csv(DATA_PATH / 'terms.csv', columns=termsFields,index=True)  
