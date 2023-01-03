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

# Tasks 

# How to get all links from BBC home page
# How to get all links that are just news articles
# Store in dataframe 
# UUID, NAME, Date, Topics
# Take random sample of five and send them as url link
# Attach them as pdf as well

# add html button to email / design the email using html & css with a nice button. 
# When the button is clicked the count increases of a field in the database
# Like count table in database with columns - userID, news, sport, music,
# each like or dislike updates this table, it also adds a new column for each new genre that they are sent 
# do we want the generes to be identified by time period (month?), and source, guardian, type of source (left wing, educational, centre, right, techy etc)

# useful links -- https://www.google.com/search?q=add+html+button+to+email+python&client=firefox-b-d&ei=i-Q2Y8_GK9OI8gKj5YLwBg&oq=add+html+button+to+email+p&gs_lcp=Cgdnd3Mtd2l6EAMYADIFCCEQoAEyBQghEKABMgUIIRCgATIECCEQFTIICCEQHhAWEB0yCAghEB4QFhAdMggIIRAeEBYQHTIICCEQHhAWEB0yCAghEB4QFhAdMggIIRAeEBYQHToKCAAQRxDWBBCwAzoFCAAQkQI6EQguEIAEELEDEIMBEMcBENEDOgsIABCABBCxAxCDAToLCC4QsQMQgwEQ1AI6CAgAELEDEIMBOgsILhCABBCxAxCDAToQCC4QsQMQgwEQxwEQ0QMQQzoECAAQQzoUCC4QgAQQsQMQgwEQxwEQ0QMQ1AI6CAguELEDEIMBOgUIABCABDoFCC4QgAQ6CAguEIAEENQCOgYIABAeEBY6BQgAEIYDSgQIQRgASgQIRhgAUM4IWJcpYJgyaANwAXgAgAGfAogB0hWSAQYyMC40LjKYAQCgAQHIAQjAAQE&sclient=gws-wiz
# https://stackoverflow.com/questions/58971749/i-want-an-upvote-button-that-when-clicked-increment-the-value-of-a-fieldinteger
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiEpcWzyLz6AhWHbcAKHd5XDzkQFnoECAcQAQ&url=https%3A%2F%2Fdocs.python.org%2F3%2Flibrary%2Ftkinter.html&usg=AOvVaw2w5EX5ZeZBD19NwlNE6Yai



################################

# next steps
# get script to run automatically every day - check 
# redesign email - check
# subscription form - check
# link up all code 

# bbc scarper script (scrapes homepage and then pushes to db)

# user_registration script (connects to google drive form spreadhseet and adds new users to db)

# send emails. (pymongo to load users and articles. for each user randomy selects an article and sends it)

# add extra acrticles (guardian, ted talk, )
# pick on article at random each day and post to redes sociales 
# amend sample to add wait according to what interests each usser has 
# record kept of articles sent? and topics? and if user liked it? 













class_search = "ssrcss-5cgi52-PromoLink e1f5wbog0"

today = datetime.today().strftime('%Y-%m-%d')
# <a href="/news/world-europe-63072113" class="ssrcss-5cgi52-PromoLink e1f5wbog0"><span role="text"><p class="ssrcss-6arcww-PromoHeadline e1f5wbog4"><span aria-hidden="false">Russia to formally annex four more areas of Ukraine</span></p></span></a>

print("Hello Javi")

URL = 'https://www.bbc.co.uk'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

links = soup.find_all("a", class_ = class_search) 

bbc = "https://www.bbc.co.uk"

# df = pd.DataFrame(columns = ['url', 'title', 'date'])

url = []
title = []
date = []

for x in links: 

	if re.search("(news|sport)", x['href']):

		url.append(bbc + x['href'])

		date.append(datetime.today().strftime('%Y-%m-%d'))

		span = x.find_all("span", role = "text")

		for t in span:
			title.append(t.text)




df = {}

df['url'] = url
df['title'] = title
df['date'] = date

df = pd.DataFrame(df)

df['uuid'] = pd.util.hash_pandas_object(df['url'], index = True)

df['split'] = df['url'].str.split("/")



############################################################

"""
test_fun removes any blank strings from the URL split. 

"""

u = ['https:', '', 'www.bbc.co.uk', 'news', 'uk-63105522']

def test_fun(U =u):
	tjk = list(filter(None, U))
	return tjk

# this = test_fun()

# print(this)

df['split'] = df['split'].apply(test_fun)

############################################################

"""
test_fun1 identifies the main topic as it is the only part of the url split without 
any special characters. 
"""


def test_fun1(U = u):
	test_list = []
	for x in U: 
		if re.search(r'\b^[a-zA-Z_]*$\b', x):
			test_list.append(x)
	return(test_list)


df['main_topic'] = df['split'].apply(test_fun1)

########################################################
"""
test_fun2 - for each part of url split, if it contains a dash then that part of the url is re-split by the dahses
this allows the secondary topics to be identified. 
"""
def test_fun2(U= u):
	test_list = []
	for x in U:
		if re.search("-", x):
			x_split = x.split("-")
			test_list.append(x_split)
	return(test_list)

#that = test_fun2()
#print(that)

df['secondary_topics'] = df['split'].apply(test_fun2)

##############################################

"""
test_fun3 removes the final part of the dash split. 
this removes the number split found at the end of each url. 
"""

def test_fun3(U = u):
	tjks = []
	for x in U:
		tjks.append(x[:-1])
	return tjks


df['secondary_topics'] = df['secondary_topics'].apply(test_fun3)

df = df.explode('secondary_topics')

df['source_name'] = "bbcnews"

df['source_website'] = URL

# df['source_hash'] = pd.util.hash_pandas_object(df[['source_name', 'source_website']], index = True)


print(df)

###################################################

os.chdir('..')

df = df.set_index('uuid')

df.to_json("daily_articles_bbc.json", orient = 'records')

daily_save_name = "daily_articles/json/bbc/" + "daily_articles_bbc_" + today + ".json"

df.to_json(daily_save_name, orient = 'records')

##############################################

# push df to mongo db

# myclient = pymongo.MongoClient("mongodb://localhost:27017/")

myclient = pymongo.MongoClient("mongodb+srv://james_attwood:7tadZOaBzo94zUeZ@avoidthealgorithm1.jsu1na6.mongodb.net/?retryWrites=true&w=majority")

db = myclient["news_db"]

Collection = db["news_articles"]

with open("daily_articles_bbc.json") as file:
	file_data = json.load(file)

if isinstance(file_data, list):
    Collection.insert_many(file_data) 
else:
    Collection.insert_one(file_data)

###############################################

# delete duplicates from database

record_hashes = set()

for record in Collection.find():
    record_id = record.pop('_id')
    record_hash = md5(dumps(record.pop('url')).encode("utf-8")).hexdigest()

    if record_hash in record_hashes:
        Collection.delete_one({'_id': record_id})
    else:
        record_hashes.add(record_hash)

for record in Collection.find({'url':{"$regex": 'bbc'}, 'date':today}):
    print(record) 