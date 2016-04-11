
# coding: utf-8

# In[5]:

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator


# In[6]:

import io 
import json
with io.open('config_secret.json') as cred:
    creds = json.load(cred)
    auth = Oauth1Authenticator(**creds)
    client = Client(auth)


# In[7]:

import psycopg2
import sys
import pprint
#Define our connection string
conn_string = "host='50.16.139.89' dbname='smart' user='dmkm' password='dmkm1234'"
# print the connection string we will use to connect
print("Connecting to database")
 # get a connection, if a connect cannot be made an exception will be raised here
conn = psycopg2.connect(conn_string)
 # conn.cursor will return a cursor object, you can use this cursor to perform queries
cursor = conn.cursor()
print("Connected!")
cursor.execute("SELECT name,id FROM ip.interest_points where in_use = '1'")
records = cursor.fetchall()


# In[8]:

import re
import unicodedata

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    text = text.replace("\'"," ")
    text = text.replace(":","")
    text = text.replace("  "," ")
    text = text[0:60]
    return str(text)

def text_to_id(text):
    """
    Convert input text to id.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-],', '', text)
    return text
#response.total
#strip_accents(records[i][0])


# In[9]:

yelp = []
for i in range(0,len(records)):
    params = {
    'term': strip_accents(records[i][0]),
    'lang': 'fr'
    }
    response = client.search('Lyon', **params)
    if response.total !=0 :
        yelp.append([response.businesses[0].name,
        response.businesses[0].rating,
        response.businesses[0].location.coordinate.latitude,
        response.businesses[0].location.coordinate.longitude,
        response.businesses[0].image_url,
        response.businesses[0].phone,
        response.businesses[0].review_count,
        records[i][1]])


# In[10]:

for row in yelp:
    name = row[0]
    rating = row[1]
    latitude = row[2]
    longitude = row[3]
    image_url = row[4]
    phone = row[5]
    review_count = row[6]
    idd = row[7]
    
    query = "INSERT INTO landing.ip_yelp (name, rating, latitude, longitude, image_url, phone, review_count, idd) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    data = (name, rating, latitude, longitude, image_url, phone, review_count, idd)
    
    cursor.execute(query,data)
    conn.commit()


# In[ ]:


