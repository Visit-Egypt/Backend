from fastapi import APIRouter, status
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.chatbot.entities.chatbot import chatBotRes,chatBotBase
from visitegypt.api.container import get_dependencies
import requests
from visitegypt.core.chatbot.services import chatbot_service
from visitegypt.config.environment import CHAT_BOT_SERVICE_URL
repo = get_dependencies().chatbot_repo



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
    except Exception as e:
        return { "response":"Chatbot is currently down" }

async def callAPI(message):
    data = {
        "message":message
    }
    response = requests.post(CHAT_BOT_SERVICE_URL, json=data)
    resu = dict(response.json())
    print(resu)
    res= await classes(resu)
    return res    

async def classes(result):
    if(result['tag'] == "Hotel"):
        if(not result['recognation']):
            return {"response":"Please Mention the Goverment"}
        city = result['recognation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_hotels_by_city(repo, city)
            response = "Here are some nice hotels in " + city + "\n"
            for i in res:
                response = response + i["Hotel_Name"] + " at " + i["Location"] + "\n"
            return {"response":response}
        except Exception as e: raise e
    elif(result['tag'] == 'search on this topic'):
        king = result['recognation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_king_by_name(repo, king)
            print(res)
            response = res['Main Title'] + " " + res['Name'] + " From The " + res['Dynasty'] + " Was " + res['Comment']
            return {"response":response}
        except Exception as e: raise e
    elif(result['tag'] == "Resturant"):
        if(not result['recognation']):
            return {"response":"Please Mention the Goverment"}
        city = result['recognation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_restaurants_by_city(repo, city)
            response = "Here are some nice restaurants in " + city + ", "
            for i in res:
                response = response + i["Restaurant_Name"] + ", "
            return {"response":response}
        except Exception as e: raise e
    elif(result['tag'] == "Clinic"):
        if(not result['recognation']):
            return {"response":"Please Mention the Goverment"}
        city = result['recognation'][0]['Name'].capitalize()
        try:
            res = await chatbot_service.get_pharmacy_by_city(repo, city)
            response = "You can check these pharmacies in " + city + "\n"
            for i in res:
                response = response + i["Name"] + " at " + i['Location'] +"\n"
            return {"response":response}
        except Exception as e: raise e
    else:
        return {"response":result['tag']}