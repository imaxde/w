from google import genai
from google.genai import types
from datetime import datetime
import requests
from pydantic import BaseModel

client = genai.Client(api_key="AIzaSyAUi8C9kyEwkivTXqxRhytTpWAh_lZ84oc")
with open("static/txt/instruction.txt") as f:
    system_instructions = f.read()


def generate(context):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=context,
        config=types.GenerateContentConfig(
            safety_settings=[
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                                    threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                                    threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                    threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                                    threshold=types.HarmBlockThreshold.BLOCK_NONE),
                types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                                    threshold=types.HarmBlockThreshold.BLOCK_NONE)
            ],
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=system_instructions),
            ]
        )
    )
    return response.text


def messages_context(msg_history, new_message):
    ai_context = []
    # response = requests.get("http://127.0.0.1:5000/api/messages")
    # data = response.json()["messages"]
    # msg_history.sort(key=lambda x: x.transaction_date)
    for i in msg_history:
        ai_context.append(types.Content(role="user", parts=[types.Part.from_text(text=i.question)]))
        ai_context.append(types.Content(role="model", parts=[types.Part.from_text(text=i.answer)]))
    ai_context.append(types.Content(role="user", parts=[types.Part.from_text(text=new_message)]))
    return ai_context
