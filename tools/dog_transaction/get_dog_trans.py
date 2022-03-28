import requests
import json
import traceback
from datetime import datetime, timedelta
from time import sleep

from loguru import logger

import mongoengine
from mongoengine import connect

from classes import Transaction, MAP
from multiprocessing.dummy import Pool as ThreadPool

from config import *

connect('dogami-database', host='127.0.0.1', port=27017)


def get_all_operation_trans(payload):
    while True:
        try: 
            response_trans_list = requests.get(LIST_TRANS_URL, params=payload)
            logger.info(f"Success list 1000 operation hash")
            return json.loads(response_trans_list.text)
        except Exception as e:
            logger.error(e)
    

def check_transaction_by_operation(operation_hash, trans_mode='sales'): 
    entrypoint = 'fulfill_ask' if trans_mode == 'sales' else 'fulfill_offer'
    
    trans_detail_url = OPERATION_PAGE + operation_hash

    loop = True
    while loop:
        try:
            response_trans_detail = requests.get(trans_detail_url)
            all_steps = json.loads(response_trans_detail.text)
            logger.info(f"Success loading trans {operation_hash}")
            loop = False
        except Exception as e:
            logger.error(f'Fail to loading detail trans {operation_hash}')

    # check if transaction is sales and sell a DOGAMI'
    # if the trans is DOG sales, there is a specific step call Transer which send DOG NFT to buyer       
    all_wallets = [step.get('target', {}).get('address', '') for step in all_steps]
    
    if DOGAMI_CONTRACT in all_wallets: 
        result = {}    
        for step in all_steps:         
            if step.get('target', {}).get('address', '') == DOGAMI_CONTRACT:
                try: 
                    result['buyer'] = step.get('parameter').get('value')[0].get('txs')[0].get('to_')
                    result['seller'] = step.get('parameter').get('value')[0].get('from_')  
                    break 
                except Exception as e:
                    # logger.info('Not step needed') 
                    pass 
        for step in all_steps:  
            if (step.get('parameter', {}).get('entrypoint', '') == entrypoint):               
                result["trans_id"] = str(step.get("id"))
                result['operation_hash'] = str(operation_hash)
                result['token_id'] = str(step.get("diffs")[0].get("content").get("value").get("token").get("token_id"))
                result['time_stamp'] = str(step.get('timestamp')) 
                result['order_type'] = str(trans_mode)
                try: 
                    result['price'] = int(int(step.get("diffs")[0].get("content").get("value").get("amount"))/1000000)
                except:
                    with open('log/fail_to_get_dog_price.txt', 'a') as f:
                        logger.error("A dog trans but cannot get price")
                        f.write('\n')
                        f.write(json.dumps({"trans_id": result['trans_id'], "time": str(datetime.now())}) )
                    result['price'] = None
                # print(result)
                logger.info(f"Found a dog trans: {operation_hash}")
                return result
        if len(result.keys()) <= 2:
            logger.error(f"A dog trans but not right format: {operation_hash}")
                
    
def save_trans(trans_info):
    if not trans_info:
        return
    
    current_id = str(trans_info.get('trans_id'))
    # print(type(current_id))
    
    a = Transaction.objects(trans_id=current_id)
    if a: 
        logger.info(f"Trans {current_id} already in db")
        return

    trans = Transaction()       
    trans.init_from_dict(trans_info=trans_info, map=MAP) 
    
    trans.save()
    logger.info(f"successful save transaction {current_id} of token {trans_info.get('token_id')}")


def get_dog_trans(type='transaction', first_trans=FIRST_CHECK_TRANS, last_check=LAST_CHECKED_TRANS, limit=1000, sort=0, tz_market_wallet=TZ_MARKET_WALLET, trans_mode='sales' ):    
    
    entrypoint = 'fulfill_ask' if trans_mode == 'sales' else 'fulfill_offer'
    print(f'Start get data of {trans_mode} ')
    
    last_id = first_trans
    count = 0
    err = 0
    start_time = datetime.now().utcnow()
    last_trans_time = start_time + timedelta(days=-1)
    
    while last_id != None and last_trans_time < start_time and last_id < last_check: 
        payload = {'type': str(type), 
                   'limit': str(limit), 
                   'sort':str(sort), 
                   'lastId': str(last_id), 
                   'initiator.ne':str(tz_market_wallet), 
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
        last_id = int(list_operation[-1].get("id"))
        last_trans_time = datetime.strptime(list_operation[-1].get("timestamp"), "%Y-%m-%dT%H:%M:%SZ")


def gen_distance(start=FIRST_CHECK_TRANS, stop=LAST_CHECKED_TRANS, step=NUM_THREAD):
    temp = []
    if step == 1:
        temp.append(start)
        temp.append(stop)
        
    step_distance = int((stop-start)/step) 
    
    while start <= stop:
        temp.append(start)
        start += step_distance
    temp.append(stop)
    print('ok')
    
    output = []
    for i in range(len(temp)-1):
        output.append(str(temp[i]) + '-' + str(temp[i+1]))
    return output


def check_sales(distance):
    first_trans = int(distance.split('-')[0])
    last_check = int(distance.split('-')[1])
    
    get_dog_trans(first_trans=first_trans, last_check=last_check, trans_mode='sales')
    # get_dog_trans(first_trans=first_trans, last_check=last_check, trans_mode='accept_offer')
    
    
def check_accept_offer(distance):
    first_trans = int(distance.split('-')[0])
    last_check = int(distance.split('-')[1])
    
    # get_dog_trans(first_trans=first_trans, last_check=last_check, trans_mode='sales')
    get_dog_trans(first_trans=first_trans, last_check=last_check, trans_mode='accept_offer')
    
           
if __name__ == '__main__':
    # sales 
    logger.add(f"log/log_sales.log", rotation="50 MB")
    with open(f"log/log_sales.log", 'w') as f:
        f.close()
    
    logger.info("Start Sales Program")
    pool = ThreadPool(NUM_THREAD)
    
    distances = gen_distance(start=FIRST_CHECK_TRANS, stop=LAST_CHECKED_TRANS, step=NUM_THREAD)
    # print(distances)
    results = pool.map(check_sales, distances)
      
    pool.close()
    logger.info("Finish Sales Program")


    # accept offer
    logger.add(f"log/log_accept_offer.log", rotation="50 MB")
    with open(f"log/log_accept_offer.log", 'w') as f:
        f.close()
    
    logger.info("Start Accept Offer Program")
    pool = ThreadPool(NUM_THREAD)
    
    distances = gen_distance(start=FIRST_CHECK_TRANS, stop=LAST_CHECKED_TRANS, step=NUM_THREAD)
    # print(distances)
    results = pool.map(check_accept_offer, distances)
    # pool.map(check_accept_offer, distances)   
    
    
    pool.close()
    logger.info("Finish Accept offer Program")
