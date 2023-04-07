import os
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder

from app.whatsapp_client import WhatsAppClient
from app.openai_client import OpenAIClient
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")


@app.get("/")
def I_am_alive():
    return "I am alive!!"

@app.get("/webhook/")
def subscribe(request: Request):
    print("We received a GET request")
    if request.query_params.get('hub.verify_token') == WHATSAPP_VERIFY_TOKEN:
        challenge = request.query_params.get('hub.challenge')
        if challenge:
            return int(challenge)
        else:
            return "Authentication failed. No challenge."
    return "Authentication failed. Invalid Token."

@app.post("/webhook/")
async def process_notifications(request: Request):
    print("We received a POST request")
    wtsapp_client = WhatsAppClient()
    data = await request.json()
    response = wtsapp_client.process_notification(data)
    if response["statusCode"] == 200:
        if response["body"] and response["from_no"]:
            openai_client = OpenAIClient()
            reply = openai_client.complete(prompt=response["body"])
            print ("\nreply is:"  + reply)
            reply = reply.replace("?\n\n", "")
            wtsapp_client.send_text_message(message=reply, phone_number=response["from_no"], )
            print ("\nreply is sent to whatsapp cloud:" + str(response))

    return jsonable_encoder({"status": "success"})