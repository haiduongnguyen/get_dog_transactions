from enum import unique
from operator import index
from mongoengine import *



class Transaction(Document):
    
    """ List attributes
    See example: https://objkt.com/asset/dogami/2124"""
    
    token_id = StringField(max_length=200)
    
    operation_hash = StringField(unique=True, max_length=200)
    
    price = IntField()
    
    time_stamp = StringField(max_length=200)

    seller = StringField(max_length=200)
    
    buyer = StringField(max_length=200)
    
    order_type = StringField(max_length=200)
    
    trans_id = StringField(index=True, max_length=200)


    def init_from_dict(self, trans_info=None, map=None ):
        self.token_id = trans_info.get(map.get('token_id'))
        self.operation_hash = trans_info.get(map.get('operation_hash'))
        self.price= trans_info.get(map.get('price'))
        self.time_stamp = trans_info.get(map.get('time_stamp'))
        self.seller = trans_info.get(map.get('seller'))
        self.buyer = trans_info.get(map.get('buyer'))
        self.order_type = trans_info.get(map.get('order_type'))
        self.trans_id = trans_info.get(map.get('trans_id'))


MAP = {
    "token_id" : "token_id" , 
    
    "operation_hash": "operation_hash" ,
    
    "price" : "price" ,

    "time_stamp" : "time_stamp" ,

    "seller" : "seller" ,

    "buyer" : "buyer" ,

    "order_type" : "order_type" ,
    
    "trans_id": "trans_id"
}
