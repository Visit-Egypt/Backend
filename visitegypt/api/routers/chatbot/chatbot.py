from fastapi import APIRouter, status
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.chatbot.entities.chatbot import chatBotRes,chatBotBase
import nltk
from visitegypt.api.container import get_dependencies
import random
import spacy 
from nltk.stem.lancaster import LancasterStemmer
import json
import requests
import os
from visitegypt.core.chatbot.services import chatbot_service
repo = get_dependencies().chatbot_repo

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
    response_model=chatBotRes,
    status_code=status.HTTP_200_OK,
    summary="recive requestes",
    tags=["Chatbot"]
)
async  def get_chatbot(message:chatBotBase):
    try:
        res = await chat(message.message)
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

async def chat(inputt):
    bag =  bag_of_words(inputt, words)
    reco =  net(inputt) 
    results_index = callAPI(str(bag).replace("]","").replace("[",""))
    tag = labels[results_index] 
    sentence = random.choice(reponses[results_index])
    result = {'response':sentence , "recogniation" : reco}
    return await classes(result)

def callAPI(message):
    data = {
        "message":message
    }
    response = requests.post(APIURL, json=data)
    print(response.json()["body"])
    return int(response.json()["body"])

async def classes(result):
    print(result)
    if(result['response'] == "Hotel"):
        if(not result['recogniation']):
            return {"response":"Please Mention the Goverment"}
        city = result['recogniation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_hotels_by_city(repo, city)
            response = "Here are some nice hotels in " + city + "\n"
            for i in res:
                response = response + i["Hotel_Name"] + " at " + i["Location"] + "\n"
            return {"response":response}
        except Exception as e: raise e
    elif(result['response'] == 'search on this topic'):
        king = result['recogniation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_king_by_name(repo, king)
            print(res)
            response = res['Main Title'] + " " + res['Name'] + " From The " + res['Dynasty'] + " Was " + res['Comment']
            return response
        except Exception as e: raise e
    elif(result['response'] == "Resturant"):
        if(not result['recogniation']):
            return {"response":"Please Mention the Goverment"}
        city = result['recogniation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_restaurants_by_city(repo, city)
            response = "Here are some nice restaurants in " + city + ", "
            for i in res:
                response = response + i["Restaurant_Name"] + ", "
            return {"response":response}
        except Exception as e: raise e
    elif(result['response'] == "Clinic"):
        if(not result['recogniation']):
            return {"response":"Please Mention the Goverment"}
        city = result['recogniation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_pharmacy_by_city(repo, city)
            response = "You can check these pharmacies in " + city + "\n"
            for i in res:
                response = response + i["Name"] + " at " + i['Location'] +"\n"
            return {"response":response}
        except Exception as e: raise e
    else:
        return {"response":result['response']}
