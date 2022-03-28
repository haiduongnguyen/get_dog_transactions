from tabnanny import check
import requests
import json
import traceback
from datetime import datetime, timedelta
from time import sleep

from loguru import logger
import mongoengine
from mongoengine import connect
from multiprocessing.dummy import Pool as ThreadPool

from classes import Transaction, MAP
from config import *


from get_dog_trans import get_all_operation_trans, check_transaction_by_operation, save_trans


connect('dogami-database', host='127.0.0.1', port=27017)


def check_real_time_trans(trans_mode):
    
    entrypoint = 'fulfill_ask' if trans_mode == 'sales' else 'fulfill_offer'
    
    last_id = 5000000000
    count = 0
    err = 0   
    checked_id = LAST_CHECKED_TRANS
    
    while checked_id < last_id:
        payload = {'type': 'transaction', 
                    'limit': 1000, 
                    'sort':0, 
                    'lastId': str(checked_id), 
                    'initiator.ne':str(TZ_MARKET_WALLET), 
                    'entrypoint':str(entrypoint)}

        list_operation = get_all_operation_trans(payload=payload)
        # list_operation = [{'hash':'onkWpu4i5aAoa42AZc2sTCQZJ5h4uXRMa3bP61EFs9Hu4j7bRrK'}]
            
        for item in list_operation:
            count += 1
            operation_hash = item.get('hash')
            try: 
                trans_info = check_transaction_by_operation(operation_hash=operation_hash, trans_mode=trans_mode)
                save_trans(trans_info=trans_info) 
            except:
                err += 1
            if count % 100 == 0:
                print(f"Finish check {count} transactions")
                print("number err:", err)
                sleep(30)
            
        # get data of next page
        checked_id = int(list_operation[-1].get("id"))
        sleep(600)


if __name__ == '__main__':
    
    logger.logger.add(f"log_real_time/log.log", rotation="50 MB")
    
    logger.info("Start get real time transaction Program")
    
    pool = ThreadPool(2)
    
    trans_modes = ['sales', 'accept_offer']
    
    results = pool.map(check_real_time_trans, trans_modes)
    