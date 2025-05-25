from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from google_calendar_gmail import list_calendar_events, send_email, get_calendar_service, search_contacts, list_gmail_labels, list_messages_by_label, get_message_details, reply_to_message, delete_message
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

class EventCreateRequest(BaseModel):
    summary: str
    start: str  # ISO format datetime string
    end: str    # ISO format datetime string
    description: str = ""
    location: str = ""

class ContactSearchRequest(BaseModel):
    query: str
    max_results: int = 10

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

@app.post("/create_event")
def create_event(req: EventCreateRequest):
    service = get_calendar_service()
    event = {
        "summary": req.summary,
        "start": {"dateTime": req.start, "timeZone": "UTC"},
        "end": {"dateTime": req.end, "timeZone": "UTC"},
        "description": req.description,
        "location": req.location,
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return {"id": created_event["id"], "htmlLink": created_event.get("htmlLink")}

class EventEditRequest(BaseModel):
    event_id: str
    summary: str = None
    start: str = None
    end: str = None
    description: str = None
    location: str = None

@app.post("/edit_event")
def edit_event(req: EventEditRequest):
    service = get_calendar_service()
    try:
        event = service.events().get(calendarId='primary', eventId=req.event_id).execute()
        if req.summary: event["summary"] = req.summary
        if req.start: event["start"]["dateTime"] = req.start
        if req.end: event["end"]["dateTime"] = req.end
        if req.description: event["description"] = req.description
        if req.location: event["location"] = req.location
        updated_event = service.events().update(calendarId='primary', eventId=req.event_id, body=event).execute()
        return {"id": updated_event["id"], "htmlLink": updated_event.get("htmlLink")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_contacts")
def search_contacts_endpoint(req: ContactSearchRequest):
    try:
        results = search_contacts(req.query, req.max_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/labels")
def get_labels():
    try:
        return list_gmail_labels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages")
def get_messages(label_id: str = 'INBOX', max_results: int = 10):
    try:
        return list_messages_by_label(label_id, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/message/{message_id}")
def get_message(message_id: str):
    try:
        return get_message_details(message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ReplyRequest(BaseModel):
    message_id: str
    reply_text: str

@app.post("/reply")
def reply_to_message_endpoint(req: ReplyRequest):
    try:
        return reply_to_message(req.message_id, req.reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DeleteRequest(BaseModel):
    message_id: str

@app.post("/delete_message")
def delete_message_endpoint(req: DeleteRequest):
    try:
        return delete_message(req.message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 