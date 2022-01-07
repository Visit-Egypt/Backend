from fastapi import APIRouter, status
from nltk.sem.evaluate import Error
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.chatbot.entities.chatbot import chatBotRes,chatBotBase
from sagemaker.tensorflow.model import TensorFlowModel
import nltk
import numpy as np
import random
import spacy 
from nltk.stem.lancaster import LancasterStemmer
import json
import requests

nltk.download('punkt')
stemmer =  LancasterStemmer()
APIURL = 'https://a9cwkzo25d.execute-api.us-east-2.amazonaws.com/prod/'

words =  ["'s", '50', 'a', 'about', 'am', 'anyon', 'ar', 'be', 'bye', 'chang', 'convert', 'dang', 'day', 'do', 'doll', 'emerg', 'find', 'forecast', 'going', 'good', 'goodby', 'hello', 'help', 'hi', 'hotel', 'how', 'i', 'in', 'is', 'it', 'know', 'lat', 'lik', 'loc', 'me', 'nee', 'next', 'now', 'pol', 'pound', 'rain', 'resta', 'right', 'see', 'sleep', 'sup', 'tel', 'temp', 'thank', 'that', 'the', 'ther', 'to', 'tomorrow', 'top', 'want', 'weath', 'what', 'you']

labels =  {0:'Hotel',1: 'Resturant',2: 'conversation',3: 'currency',4: 'goodbye',5: 'greeting',6: 'info',7: 'police',8:'thanks',9:'weather'}
reponses = { 0 : ["Four Seasons Hotel Cairo at the First Residence(35 Giza Street, Giza 12311 Egypt), Marriott Mena House(6 Pyramids Road, Giza 12556 Egypt) , Great Pyramid Inn(14 Abou Al Hool Street, Giza Egypt)"],
1:["The Blue Restaurant & Grill (12 Ahmed Ragheb Street Garden City, Cairo 11519 Egypt),Culina(1113 Corniche El Nil Street The Nile Ritz-Carlton, Downtown, Cairo 11221 Egypt),Saigon Restaurant & Lounge(2005 B, Corniche El Nil Fairmont Towers Nile City - 2005 B, Corniche El Nil, Ramlet Beaulac, Cairo 2466 Egypt)"],
2:["good hope you are as well"],
3:["Currency"],
4: ["See you later thanks for visiting", "Have a nice day", "Bye! Come back again soon."],
5: ["Hello, thanks for visiting", "Good to see you again", "Hi there, how can I help?"] , 
6: ["search on this topic"],
7: ["call the police on 122"],
8 : ["Happy to help!", "Any time!", "My pleasure" ,"You are welcome"] ,
9: ["weather"]}

model_entity =  spacy.load('en_core_web_sm')

router = APIRouter(responses=generate_response_for_openapi("Chatboot"))

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="recive requestes",
    tags=["Chatboot"]
)
def get_chatbot(message:chatBotBase):
    print(message)
    try:
        res = chat(message.message)
        return res
    except Error:
        return Error

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    return bag

def net(word) :
    sentnece = [{"response": "" , "reco": ""}]
    for ent in model_entity(word).ents:
        sentnece[0]["reco"]=ent.text
    return sentnece

def chat(inputt):
    bag =  bag_of_words(inputt, words)
    sentnece =  net(inputt) 
    print(sentnece)
    print(bag)
    results_index = callAPI(str(bag).replace("]","").replace("[",""))
    print(results_index)
    tag = labels[results_index] 
    if  results_index == 3 :
         curr = sentnece[0]["reco"]
         curr =  curr.split(' ')[0]
         sentnece[0]['response'] =  int(curr) *16
         sentnece[0]["reco"] =  'Money '
         return sentnece
    else:
       sentnece[0]['response'] = random.choice(reponses[results_index])
       return sentnece

def callAPI(message):
    data = {
        "message":message
    }
    response = requests.post(APIURL, json=data)
    print(response.json()["body"])
    return int(response.json()["body"])