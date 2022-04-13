import logging
from pprint import pprint
import numpy as np
import requests
import json

import mongoengine
from mongoengine import connect

from param import QUERY
from classes import Dog, MAP
from multiprocessing.dummy import Pool as ThreadPool

API_URL = 'https://data.objkt.com/v2/graphql'


# connect('dogami-database', host='127.0.0.1', port=27017)
connect('dogami-database', host='127.0.0.1', username="abc", password="abc", port=27017)



def get_data(query=None, variables=None):
    loop = True
    while loop:
        try: 
            response = requests.post(url=API_URL, json={'query': query, 'variables': variables})
            response_context = json.loads(response.text)
        
            # pprint(response_context)
            return response_context
        except Exception as e:
            with open('res_error.txt', 'a') as f:
                f.write('\n')
                f.write(response.text)
                f.write('\n')

        

def save_data(response_context=None, variables=None, port=27017):

    # db = client[db_name]
    # collection = db.dog_collection

    if not response_context: 
        logging.info("No data to save")
        with open('error.txt', 'a') as f:
            f.write('\n')
            f.write(str(variables.get("tokenId")))
        return None
    
    attributes = response_context['data']['token'][0]['attributes']
    # print(attributes)

    dog_info = {}

    dog_info['token_id'] = variables.get('tokenId')

    for attr in attributes :
        key = attr.get('attribute').get('name')
        value = attr.get('attribute').get('value')  
        dog_info[key] = value
        # pprint(dog_info)  

    # collection.insert_one(document=dog_info)

    # logging.info("Successful save data")
    
    dog = Dog()
    dog.init_from_dict(dog_info=dog_info, map=MAP)
    
    dog.save()
    print(variables['tokenId'])
    print(variables)
    
    # return "Done"


def get_dog(token_id):

    already_in_db = False
    try: 
        Dog.objects.get(token_id=token_id)
        already_in_db = True
    except:
        pass
    # print(already_in_db)
    if already_in_db:
        print("already in db")
        return    
    
    try:             
        variables = {"tokenId": str(token_id), "fa2": "KT1NVvPsNDChrLRH5K2cy6Sc9r1uuUwdiZQd"}
               
        response_context = get_data(query=QUERY, variables=variables)
        save_data(response_context=response_context, variables=variables)
    except :
        with open('error.txt', 'a') as f:
            f.write('\n')
            f.write(str(variables.get("tokenId")))


if __name__ == '__main__':
    
    # drop old records
    x = Dog.delete_many({})
    print(x.deleted_count, " documents deleted.")
    
    tokens_list = list(np.arange(0,8000))
    
    pool = ThreadPool(100)
    results = pool.map(get_dog, tokens_list)
    
    pool.close()
    pool.join()

