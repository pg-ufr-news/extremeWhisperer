import pandas as pd
import numpy as np

from pathlib import Path
import os
import os.path
import io
#import requests
import glob

import time
from datetime import datetime
from dateutil import parser
from datetime import date, timedelta, datetime, timezone

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
#from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import axes3d, Axes3D
import matplotlib.cm as cm

import plotly.graph_objects as go
import plotly.io as pio

pio.orca.config.use_xvfb = True

DATA_PATH = Path.cwd()
if(not os.path.exists(DATA_PATH / 'csv')):
    os.mkdir(DATA_PATH / 'csv')
if(not os.path.exists(DATA_PATH / 'img')):
    os.mkdir(DATA_PATH / 'img')

def getAge(dateString):
    today = datetime.now(timezone.utc)
    timeDate = -1
    pubDate = None
    try:
        pubDate = parser.parse(dateString)
    except:
        print('date parse error 1')
    if(not pubDate):
      try:
        pubDate = parser.isoparse(dateString)
      except:
        print('date parse error 2')   
    if(pubDate):
        timeDate = today - pubDate
        timeDate = timeDate.days 
    return timeDate

def getNewsFiles():
    fileName = './cxsv/news_????_??.csv'
    files = glob.glob(fileName)
    return files  

def getNewsDFbyList(files):    
    newsDF = pd.DataFrame(None)
    for file in files:
        #print(file)
        df = pd.read_csv(file, delimiter=',')
        if(newsDF.empty):
            newsDF = df
        else:
            newsDF = pd.concat([newsDF, df])
    if(not newsDF.empty):
        newsDF = newsDF.sort_values(by=['published'], ascending=True)        
    return newsDF 

def getNewsDF():
    files = getNewsFiles()
    newsDF = getNewsDFbyList(files)
    return newsDF     

newsDf = getNewsDF()
if(not newsDf.empty):
  newsDf['age'] = newsDf['published'].apply(
    lambda x: 
        getAge(x)
  )
  newsDf = newsDf[(newsDf.age>0) & (newsDf.age < 60)]

newsDf['count'] = 1

topicColors = {'Thunderstorm':'#53785a', 'Flood':'#030ba1', 'Storm':'#222222', 'Storm Surge':'#834fa1', 'Flash Flood':'#0245d8', 'Precipitation':'#608D3A',
               'Tsunami':'#690191', 'Drought':'#572c03', 'Earthquake':'#870047', 'Landslide':'#1C4840', 'Cold Wave':'#a7e9fa', 'Heat Wave':'#d85212', 'Iceberg':'#02b5b8',
               'Tropical Cyclone':'#4f7fbf', 'Volcano':'#b83202', 'Snow Avalanche':'#deddd5', 'unknown':'#d60d2b', 'Wildfire':'#fa0007', 'Fog':'#535271'  
               }
#'Insect Infestation', #Ice,Snow(meteo) #348A93

continentColors = {'unknown':'#d60d2b', 'Asia':'#ffff00', 'Europe':'#ff00ff', 'North-America':'#0000ff', 'Africa':'#ff0000', 'South-America':'#00ff00', 'Oceania':'#00ffff'}
feedColors = {'unknown':'#d60d2b', 'wmo':'#ff0000', 'meteo':'#008888', 'effis':'#00ff00', 'relief':'#880088', 'edo':'#0000ff', 'fema':'#888800', 'eonet':'#ffff00', 'usgs':'#ffff88', 'eswd':'#ff00ff', 'floodlist':'#ff88ff', 'random':'#00ffff'}


def hexToRgba(hexa, a=0.6):
  hexa = hexa.replace('#','')
  rgba = 'rgba('
  for i in (0, 2, 4):
    decimal = int(hexa[i:i+2], 16)
    rgba+=(str(decimal)+',')
  rgba+=(str(a)+')') 
  return rgba

def getHazardColor(haz):
    colorImp = 'rgba(0,0,0,0.8)'
    if(haz in topicColors):
       colorImp = hexToRgba(topicColors[haz])
    return colorImp    

def getContinentColor(haz):
    colorImp = 'rgba(0,0,0,0.8)'
    if(haz in continentColors):
       colorImp = hexToRgba(continentColors[haz])
    return colorImp  

def getFeedColor(haz):
    colorImp = 'rgba(0,0,0,0.8)'
    if(haz in feedColors):
       colorImp = hexToRgba(feedColors[haz])
    return colorImp  


def aggregatedDiagram(agg): 

        topicsDF = newsDf.groupby([agg], as_index=False).agg({'count':'sum'})
        topicsDF = topicsDF.sort_values(by=['count'], ascending=False)
        topicsDF.to_csv(DATA_PATH / 'csv' / ("counted_"+agg+".csv"), index=True)

        labelSize = 1000/max(min(len(topicsDF['count']),100),20)
        # Bar 
        y_pos = np.arange(len(topicsDF['count']))
        plt.rcdefaults()
        fig, ax = plt.subplots(figsize=(40, 20))
        ax.barh(y_pos, topicsDF['count'], align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(topicsDF[agg], fontsize=labelSize)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Number', fontsize=36)
        plt.xticks(fontsize=36)
        ax.set_title(agg, fontsize=48)
        plt.tight_layout()
        plt.savefig(DATA_PATH / 'img' / ('counted_'+agg+'.png'))
        plt.close('all')
        return topicsDF


colorsHazArray = []
colorsContArray = []
colorsFeedArray = []
for index, column in newsDf.iterrows():
  colorHaz = getHazardColor(column['topic'])
  colorsHazArray.append(colorHaz)

  colorCon = getContinentColor(column['continent'])
  colorsContArray.append(colorCon)

  colorFeed = getFeedColor(column['feed'])
  colorsFeedArray.append(colorFeed)

sortedTopics = aggregatedDiagram('topic') 
sortedFeeds = aggregatedDiagram('feed') 
sortedCountries = aggregatedDiagram('country') 
sortedContinents = aggregatedDiagram('continent') 
sortedIpccs = aggregatedDiagram('ipcc') 

topicDim = go.parcats.Dimension(
    values=newsDf['topic'],
    categoryorder='array',
    categoryarray = list(sortedTopics['topic']),
    label="Topic"
)
feedDim = go.parcats.Dimension(
    values=newsDf['feed'],
    categoryorder='array',
    categoryarray = list(sortedFeeds['feed']),
    label="Feed"
)
countryDim = go.parcats.Dimension(
    values=newsDf['country'],
    categoryorder='array',
    categoryarray = list(sortedCountries['country']),
    label="Country"
)
continentDim = go.parcats.Dimension(
    values=newsDf['continent'],
    categoryorder='array',
    categoryarray = list(sortedContinents['continent']),
    label="Continent"
)
ipccDim = go.parcats.Dimension(
    values=newsDf['ipcc'],
    categoryorder='array',
    categoryarray = list(sortedIpccs['ipcc']),
    label="IPCC"
)
from xvfbwrapper import Xvfb

with Xvfb() as xvfb:

  fig = go.Figure(data=[go.Parcats(
    line={'shape': 'hspline', 'color': colorsHazArray},
    dimensions=[feedDim, topicDim, continentDim, ipccDim],
    #dimensions=[feedDim, topicDim],
    arrangement='freeform',
    bundlecolors=True,
    tickfont={'size': 24},
    labelfont={'size': 28}
  )])
  ts = int(time.time())
  toDay = datetime.utcfromtimestamp(ts).strftime('%Y-%m')
  fig.update_layout(title_text="Extremes "+toDay, font_size=32)
  #fig.show()
  fig.write_image(DATA_PATH / "img" / "parcats_extremes.png", width=2400, height=1200, engine="kaleido")

  fig = go.Figure(data=[go.Parcats(
    line={'shape': 'hspline', 'color': colorsContArray},
    dimensions=[feedDim, topicDim, continentDim, ipccDim],
    #dimensions=[feedDim, topicDim],
    arrangement='freeform',
    bundlecolors=True,
    tickfont={'size': 24},
    labelfont={'size': 28}
  )])
  ts = int(time.time())
  toDay = datetime.utcfromtimestamp(ts).strftime('%Y-%m')
  fig.update_layout(title_text="Extremes "+toDay, font_size=32)
  #fig.show()
  fig.write_image(DATA_PATH / "img" / "parcats_continents.png", width=2400, height=1200, engine="kaleido")

  fig = go.Figure(data=[go.Parcats(
    line={'shape': 'hspline', 'color': colorsFeedArray},
    dimensions=[feedDim, topicDim, continentDim, ipccDim],
    #dimensions=[feedDim, topicDim],
    arrangement='freeform',
    bundlecolors=True,
    tickfont={'size': 24},
    labelfont={'size': 28}
  )])
  ts = int(time.time())
  toDay = datetime.utcfromtimestamp(ts).strftime('%Y-%m')
  fig.update_layout(title_text="Extremes "+toDay, font_size=32)
  #fig.show()
  fig.write_image(DATA_PATH / "img" / "parcats_feeds.png", width=2400, height=1200, engine="kaleido")




