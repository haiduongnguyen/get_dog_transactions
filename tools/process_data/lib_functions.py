import pandas as pd
from pymongo import MongoClient
from mongoengine import connect
import traceback
import logging
import os


def connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    try: 
        if username and password:
            mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
            conn = MongoClient(mongo_uri)
        else:
            conn = MongoClient(host, port)
        return conn[db]
    except: 
        try: 
            connect('dogami-database', host=os.getenv('MONGO_HOST', "localhost"), username=username, password=password, port=27017)
        except Exception as e:
            print("Cannot connect to mongo database")


def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df