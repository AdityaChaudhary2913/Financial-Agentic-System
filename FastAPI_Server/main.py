from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from vertexai import agent_engines
from firebase_manager import FirebaseManager

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Initialize FirebaseManager
firebase_manager = FirebaseManager(
    credential_path="../multiagentfintech-firebase-adminsdk-fbsvc-7864e9d383.json",
    database_url="https://multiagentfintech-default-rtdb.asia-southeast1.firebasedatabase.app",
)

class Message(BaseModel):
    user_id: str
    session_id: str
    query: str

@app.post("/add_message/")
async def add_message(message: Message):
    try:
        chat_data = {
            "query_user": message.query,
            "llm_response": None,
            "timestamps": {".sv": "timestamp"},
        }
        firebase_manager.save_chat_history(
            user_id=message.user_id,
            session_id=message.session_id,
            chat_data=chat_data
        )
        agent = agent_engines.get(
            "projects/high-tenure-465011-b2/locations/us-central1/reasoningEngines/RESOURCE_ID"
        )
        response = agent.query(input=f"{message.query}")
        llm_data = {
            "query_user": message.query,
            "llm_response": response,
            "timestamps": {".sv": "timestamp"},
        }
        firebase_manager.save_chat_history(
            user_id=message.user_id, session_id=message.session_id, chat_data=llm_data
        )
        return {"status": "success", "message": "Message added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
