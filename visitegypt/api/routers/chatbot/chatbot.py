from fastapi import APIRouter, status
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.chatbot.entities.chatbot import chatBotRes,chatBotBase
from visitegypt.api.container import get_dependencies
import requests
from visitegypt.core.chatbot.services import chatbot_service
repo = get_dependencies().chatbot_repo

APIURL = 'http://20.124.230.10:8000/chat'

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
        res = await callAPI(message.message)
        return res
    except:
        return {
            "response":"Chatbot is currently down"
        }

async def callAPI(message):
    data = {
        "message":message
    }
    response = requests.post(APIURL, json=data)
    resu = dict(response.json())
    print(resu)
    res= await classes(resu)
    print(res)
    return res    

async def classes(result):
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
            return {"response":response}
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