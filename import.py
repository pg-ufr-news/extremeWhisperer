import mysecrets
import os
import codecs
import io
import requests
import pandas as pd
from pathlib import Path
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
termsFields = ["index","module", "topic", "color", "feed", "term", "created", "country", "ratio", "counter", "pages", "language", "ipcc", "continent"]
topicsDict = {}

def importTerms():
    termsDF = pd.read_csv(DATA_PATH / 'terms.csv', delimiter=',')  #,index_col='keyword'
    termsDF = termsDF.sort_values(by=['ratio'], ascending=False)  
    ##print(termsDF.head())

    ghToken = os.getenv('GITHUB_TOKEN')
    if(ghToken == 'ghp_1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f'): 
        print('Please set GITHUB_TOKEN in file: mysecrets.py');
        return None

    stream=requests.get('https://raw.githubusercontent.com/newsWhisperer/extremes/main/csv/topics.csv', headers={"Authorization":"token "+ghToken}).content
    topicsDF=pd.read_csv(io.StringIO(stream.decode('utf-8')), delimiter=',')

    topicsDF['color'] = topicsDF['topic'].apply(
      lambda x: topicColors[x] if (x in topicColors) else topicColors['unknown'] 
    )
    topicsDF['pages'] = 2
    topicsDF['counter'] = 0
    topicsDF['created'] = topicsDF['added']
    ##print(topicsDF.head())

    for index, column in topicsDF.iterrows():
        if(not column['index'] in list(termsDF['index'])):
          termsDF = termsDF.append(column, ignore_index=True)
        ##else:
        ##  print('found') 

    termsDF = termsDF.sort_values(by=['ratio'], ascending=False)
    ##print(termsDF.head())
    termsDF.to_csv(DATA_PATH / 'terms.csv', columns=termsFields,index=False)  
 

importTerms()
