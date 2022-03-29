import logging
from pprint import pprint
import requests
import json
import traceback
from datetime import datetime, timedelta
from time import sleep

import loguru
import mongoengine
from mongoengine import connect

from classes import Transaction, MAP
from multiprocessing.dummy import Pool as ThreadPool


connect('dogami-database', host='127.0.0.1', port=27017)

ACCOUNT_PAGE = "https://api.tzkt.io/v1/accounts/"

OPERATION_PAGE = 'https://api.tzkt.io/v1/operations/'

TZ_MARKET_WALLET = 'KT1WvzYHCNBvDSdwafTHv7nJ1dWmZ8GCYuuC'

DOGAMI_CONTRACT = 'KT1NVvPsNDChrLRH5K2cy6Sc9r1uuUwdiZQd'

LIST_TRANS_URL = ACCOUNT_PAGE + TZ_MARKET_WALLET + '/' + 'operations' 

FIRST_DOG_TRANS = 177404585

NUM_THREAD = 1


def get_all_operation_trans(payload):
    response_trans_list = requests.get(LIST_TRANS_URL, params=payload)
    # pprint(r.text)
    return json.loads(response_trans_list.text)


def check_transaction_by_operation(operation_hash, mode='sales'): 
    entry_point = 'fulfill_ask' if mode == 'sales' else 'fulfill_offer'
    
    trans_detail_url = OPERATION_PAGE + operation_hash

    response_trans_detail = requests.get(trans_detail_url)

    # check if transaction is sales and sell a DOGAMI'
    # if the trans is DOG sales, there is a specific step call Transer which send DOG NFT to buyer
    try: 
        all_steps = json.loads(response_trans_detail.text)
        
        all_wallets = [step.get('target', {}).get('address', '') for step in all_steps]
        
        if DOGAMI_CONTRACT in all_wallets: 
            for step in all_steps:       
                if step.get('target', {}).get('address', '') == DOGAMI_CONTRACT:
                    try: 
                        result['buyer'] = step.get('parameter').get('value')[0].get('txs')[0].get('to_')
                        result['seller'] = step.get('parameter').get('value')[0].get('from_')   
                    except Exception as e:
                        print(e)   
                if (step.get('parameter', {}).get('entrypoint', '') == entry_point):
                    result = {}
                    result["trans_id"] = str(step.get("id"))
                    result['operation_hash'] = operation_hash
                    result['token_id'] = step.get("diffs")[0].get("content").get("value").get("token").get("token_id")
                    result['time_stamp'] = step.get('timestamp')   
                    result['order_type'] = mode
                    try: 
                        result['price'] = int(step.get("diffs")[0].get("content").get("value").get("amount"))/1000000
                    except:
                        with open('fail_to_get_dog_price.txt', 'a') as f:
                            f.write(json.dumps({"trans_id": result['trans_id']}) )
                        result['price'] = None
                    # print(result)
                    return result
    except Exception as e:
        logging.error(e)
        print(e)
        print(traceback.format_exc())
    return 

    
def save_trans(trans_info):
    if not trans_info:
        return
    
    current_id = str(trans_info.get('trans_id'))
    print(type(current_id))
    
    a = Transaction.objects(trans_id=current_id)
    if a: 
        return

    trans = Transaction()       
    trans.init_from_dict(trans_info=trans_info, map=MAP) 
    
    trans.save()
    print(f"successful save transaction of token {trans_info.get('token_id')}")


def get_dog_trans(type='transaction', first_trans=FIRST_DOG_TRANS, limit=1000, sort=0, tz_market_wallet=TZ_MARKET_WALLET, mode='sales', last_check=FIRST_DOG_TRANS):    
    if mode == 'sales':
        entrypoint='fulfill_ask'
    elif mode == 'accept_offer':
        entrypoint = 'fulfill_offer'
    print(f'Start get data of {mode} ')
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
                trans_info = check_transaction_by_operation(operation_hash=operation_hash, mode=mode)
                save_trans(trans_info=trans_info) 
            except:
                err += 1
            if count % 100 == 0:
                print(f"Finish check {count} transactions")
                print("number err:", err)
                sleep(5)
            
        # get data of next page
        last_id = int(list_operation[-1].get("id"))
        last_trans_time = datetime.strptime(list_operation[-1].get("timestamp"), "%Y-%m-%dT%H:%M:%SZ")


def gen_distance(start=177404585, stop=191527939, step=NUM_THREAD):
    temp = []
    if step == 1:
        temp.append(start)
        temp.append(stop)
        
    step_distance = int((stop-start)/step) 
    
    while start <= stop:
        temp.append(start)
        start += step_distance
    print('ok')
    
    output = []
    for i in range(len(temp)-1):
        output.append(str(temp[i]) + '-' + str(temp[i+1]))
    return output


def main(distance):
    first_trans = int(distance.split('-')[0])
    last_check = int(distance.split('-')[1])
    
    get_dog_trans(first_trans=first_trans, last_check=last_check, mode='sales')
    
           
if __name__ == '__main__':
    
    # pool = ThreadPool(NUM_THREAD)
    
    # distances = gen_distance(start=177404585, stop=191527939, step=NUM_THREAD)
    # results = pool.map(main, distances)   
    
    # pool.close()
    # list_operation = [{'hash':'onkWpu4i5aAoa42AZc2sTCQZJ5h4uXRMa3bP61EFs9Hu4j7bRrK'}]

    # for item in list_operation:
    #     operation_hash = item.get('hash')
    #     try: 
    #         trans_info = check_transaction_by_operation(operation_hash=operation_hash, mode='sales')
    #         save_trans(trans_info=trans_info) 
    #     except Exception as e:
    #         print(e)
    #         print(traceback.format_exc())
        
    # # get data of next page
    # last_id = int(list_operation[-1].get("id"))
    # last_trans_time = datetime.strptime(list_operation[-1].get("timestamp"), "%Y-%m-%dT%H:%M:%SZ")


    total_vol = Transaction.objects.sum('price')
    print(total_vol)
    
