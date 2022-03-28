import logging
from pprint import pprint
import numpy as np
import requests
import json

import mongoengine
from mongoengine import connect

from other_param import QUERY
from classes import Dog, MAP
from multiprocessing.dummy import Pool as ThreadPool

connect('dogami-database', host='127.0.0.1', port=27017)


# print(Dog.objects.get(token_id=46))
variables = {"tokenId": 2, "fa2": "KT1NVvPsNDChrLRH5K2cy6Sc9r1uuUwdiZQd"}


with open('error.txt', 'a') as f:
    f.write('\n')
    f.write(str(variables.get("tokenId")))
    


