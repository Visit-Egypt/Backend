from fastapi import APIRouter, status
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.chatbot.entities.chatbot import chatBotRes,chatBotBase
import nltk
import random
import spacy 
from nltk.stem.lancaster import LancasterStemmer
import json
import requests
import os

nltk.download('punkt')
stemmer =  LancasterStemmer()
APIURL = 'https://ee78syuuu9.execute-api.us-east-2.amazonaws.com/prod'

words = ["'s", '50', 'a', 'about', 'am', 'anyon', 'ar', 'be', 'bye', 'chang', 'clin', 'convert', 'dang', 'day', 'do', 'doll', 'eat', 'emerg', 'euro', 'find', 'forecast', 'going', 'good', 'goodby', 'hello', 'help', 'hi', 'hotel', 'how', 'i', 'in', 'is', 'it', 'know', 'lat', 'lik', 'loc', 'me', 'medicin', 'nee', 'next', 'now', 'pol', 'pound', 'rain', 'resta', 'right', 'see', 'sleep', 'sup', 'tel', 'temp', 'thank', 'that', 'the', 'ther', 'to', 'tomorrow', 'top', 'want', 'weath', 'what', 'you']
labels =  {0:'Clinic' ,1:'Hotel',2: 'Resturant',3: 'conversation',4: 'currency',5: 'goodbye',6: 'greeting',7: 'info',8: 'police',9:'thanks',10:'weather'}
reponses = {0:['Clinic'] ,
1 : ["Hotel"],
2:["Resturant"],
3:["good hope you are as well"],
4:["Currency"],
5: ["See you later thanks for visiting", "Have a nice day", "Bye! Come back again soon."],
6: ["Hello, thanks for visiting", "Good to see you again", "Hi there, how can I help?"] , 
7: ["search on this topic"],
8: ["call the police on 122"],
9 : ["Happy to help!", "Any time!", "My pleasure" ,"You are welcome"] ,
10: ["weather"]}

model_entity =  spacy.load('./visitegypt/api/routers/chatbot/visit_egypt')

router = APIRouter(responses=generate_response_for_openapi("Chatbot"))

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="recive requestes",
    tags=["Chatbot"]
)
def get_chatbot(message:chatBotBase):
    try:
        res = chat(message.message)
        return res
    except:
        return {
            "response":"Chatbot is currently down"
        }

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    return bag

def  net(text):
    doc = model_entity(text)
    result = []
    for ent in doc.ents:
        result.append({"Name": ent.text , "Label": ent.label_})
    return result

def chat(inputt):
    bag =  bag_of_words(inputt, words)
    reco =  net(inputt) 
    results_index = callAPI(str(bag).replace("]","").replace("[",""))
    tag = labels[results_index] 
    sentence = random.choice(reponses[results_index])
    result = {'tag':sentence , "recogniation " : reco}
    return result

def callAPI(message):
    data = {
        "message":message
    }
    response = requests.post(APIURL, json=data)
    print(response.json()["body"])
    return int(response.json()["body"])
