import logging
import requests
import json

import pymongo
from pymongo import MongoClient

from other_param import QUERY, VARS


def get_data(query=None, vars=None):
    try: 
        URL = 'https://data.objkt.com/v2/graphql'

        response = requests.post(url=URL, json={'query': query, 'variables': vars})

        response_context = json.loads(response.text)
        return response_context
    except Exception as e:
        logging.error("Error: ", e)
        return None
        

def save_data(db_name='dogami-database', response_context=None, port=27017):
    # init Mongo client, db, collection
    client = MongoClient()
    client = MongoClient('localhost', port=port)
    db = client[db_name]
    collection = db.dog_collection

    if not response_context: 
        logging.info("No data to save")
        return None
    
    attributes = response_context['data']['token'][0]['attributes']

    dog_info = {}

    dog_info['tokenId'] = VARS['tokenId']

    for attr in attributes :
        key = attr.get('attribute').get('name')
        value = attr.get('attribute').get('value')
        
        dog_info[key] = value
               
    # print(type(attributes))
    collection.insert_one(document=dog_info)

    logging.info("Successful save data")
    
    return "Done"


if __name__ == '__main__':
    
    response_context = get_data(query=QUERY, vars=VARS)
    
    save_data(response_context=response_context)
    
    
    