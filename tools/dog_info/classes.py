from enum import unique
from operator import index
from mongoengine import *



class Dog(Document):
    
    """ List attributes
    See example: https://objkt.com/asset/dogami/2124"""
    
    token_id = IntField(unique=True, index=True)
    
    generation = StringField(max_length=200)

    strength = IntField()

    intelligence = IntField()

    breeding_count = IntField()

    gender = StringField(max_length=200)

    size = StringField(max_length=200)

    status = StringField(max_length=200)

    friendliness = IntField()

    breed = StringField(max_length=200)

    group = StringField(max_length=200)

    obedience = StringField(max_length=200)

    rarity_tier = StringField(max_length=200)

    eyes_color = StringField(max_length=200)
    
    bonding_level = IntField()

    primary_personality = StringField(max_length=200)

    vitality = IntField(max_length=200)

    rarity_score = IntField()

    secondary_personality = StringField(max_length=200)

    fur_color = StringField(max_length=200)

    birthday = StringField(max_length=200)


    def init_from_dict(self, dog_info, map):
        self.token_id = dog_info.get(map.get('token_id'))
        self.generation = dog_info.get(map.get('generation'))
        self.strength = dog_info.get(map.get('strength'))
        self.intelligence = dog_info.get(map.get('intelligence'))
        self.breeding_count = dog_info.get(map.get('breeding_count'))
        self.gender = dog_info.get(map.get('gender'))
        self.size = dog_info.get(map.get('size'))
        self.status = dog_info.get(map.get('status'))
        self.friendliness = dog_info.get(map.get('friendliness'))
        self.breed = dog_info.get(map.get('breed'))
        self.group = dog_info.get(map.get('group'))
        self.obedience = dog_info.get(map.get('obedience'))
        self.rarity_tier = dog_info.get(map.get('rarity_tier'))
        self.eyes_color = dog_info.get(map.get('eyes_color'))
        self.bonding_level = dog_info.get(map.get('bonding_level'))
        self.primary_personality = dog_info.get(map.get('primary_personality'))
        self.vitality = dog_info.get(map.get('vitality'))
        self.rarity_score = dog_info.get(map.get('rarity_score'))        
        self.secondary_personality = dog_info.get(map.get('secondary_personality'))
        self.fur_color = dog_info.get(map.get('fur_color'))      
        self.birthday = dog_info.get(map.get('brithday'))



MAP = {
    "token_id" : 'token_id', 
    
    "generation" : "Generation" ,

    "strength" : "Strength" ,

    "intelligence" : "Intelligence" ,

    "breeding_count" : "Breeding count" ,

    "gender" : "Gender" ,

    "size" : "Size" ,
    
    "status" : "Status" , 

    "friendliness" : "Friendliness" ,

    "breed" : "Breed" ,

    "group" : "Group" ,

    "obedience" : "Obedience" , 

    "rarity_tier" : "Rarity tier" ,

    "eyes_color" : "Eyes color" ,
    
    "bonding_level": "Bonding level",

    "primary_personality" : "Primary personality" , 

    "vitality" : "Vitality" ,

    "rarity_score" : "Rarity score" ,

    "secondary_personality" : "Secondary personality" ,

    "fur_color" : "fur_color" ,

    "birthday" : "birthday" ,
}
