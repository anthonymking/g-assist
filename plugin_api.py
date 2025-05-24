from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from google_calendar_gmail import list_calendar_events, send_email
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Google Calendar & Gmail Plugin",
    description="A plugin to access Google Calendar events and send emails via Gmail.",
    version="1.0.0",
    servers=[
        {"url": "https://g-assist-byy8.onrender.com", "description": "Production server"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    to: str
    subject: str
    message_text: str

class Event(BaseModel):
    start: str
    summary: str

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Render!"}

@app.get("/events", response_model=List[Event])
def get_events(max_results: int = 10):
    """Get upcoming Google Calendar events."""
    try:
        events = list_calendar_events(max_results)
        return [
            Event(
                start=event['start'].get('dateTime', event['start'].get('date')),
                summary=event.get('summary', '')
            ) for event in events
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_email")
def send_email_endpoint(req: EmailRequest):
    """Send an email via Gmail."""
    try:
        result = send_email(req.to, req.subject, req.message_text)
        if result:
            return {"status": "success", "message_id": result.get('id')}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 