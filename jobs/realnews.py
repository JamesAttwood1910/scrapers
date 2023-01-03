# Packages
import requests
from bs4 import BeautifulSoup
import urllib3.request,sys,time
import pandas as pd
import pdfkit
import html2text
from docx import Document
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import yagmail
import re
from datetime import datetime
import hashlib
from termcolor import colored
import pymongo
import json
from hashlib import md5
from bson.json_util import dumps
import numpy as np

today = datetime.today().strftime('%Y-%m-%d')
# <a href="/news/world-europe-63072113" class="ssrcss-5cgi52-PromoLink e1f5wbog0"><span role="text"><p class="ssrcss-6arcww-PromoHeadline e1f5wbog4"><span aria-hidden="false">Russia to formally annex four more areas of Ukraine</span></p></span></a>

print("Hello Javi")

class_search = "entry-title"

URL = 'https://therealnews.com/'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

links = soup.find_all("h2", class_ = class_search)

url = []
title = []
date = []

for h2 in links:
	for a in h2.find_all("a"):
		url.append(a['href'])
		date.append(datetime.today().strftime('%Y-%m-%d'))
		title.append(a.text)

df = {}

df['url'] = url
df['title'] = title
df['date'] = date

df = pd.DataFrame(df)

df['uuid'] = pd.util.hash_pandas_object(df['url'], index = True)

df['split'] = df['url'].str.split("/")

df['main_topic'] = 'news'

df['source_name'] = "therealnews"

df['source_website'] = 'https://therealnews.com/'

# df['source_hash'] = pd.util.hash_pandas_object(df[['source_name', 'source_website']], index = True)


print(df.head())

################################################

os.chdir('..')

df = df.set_index('uuid')

df.to_json("daily_articles_realnews.json", orient = 'records')

daily_save_name = "daily_articles/json/realnews/" + "daily_articles_realnews" + today + ".json"

df.to_json(daily_save_name, orient = 'records')

##########################################################

# myclient = pymongo.MongoClient("mongodb://localhost:27017/")

myclient = pymongo.MongoClient("mongodb+srv://james_attwood:7tadZOaBzo94zUeZ@avoidthealgorithm1.jsu1na6.mongodb.net/?retryWrites=true&w=majority")

db = myclient["news_db"]

Collection = db["news_articles"]

with open("daily_articles_realnews.json") as file:
	file_data = json.load(file)

if isinstance(file_data, list):
    Collection.insert_many(file_data) 
else:
    Collection.insert_one(file_data)

##########################################################
record_hashes = set()

for record in Collection.find():
    record_id = record.pop('_id')
    record_hash = md5(dumps(record.pop('url')).encode("utf-8")).hexdigest()

    if record_hash in record_hashes:
        Collection.delete_one({'_id': record_id})
    else:
        record_hashes.add(record_hash)

for record in Collection.find({'url':{"$regex": 'therealnews'}, 'date':today}):
    print(record) 