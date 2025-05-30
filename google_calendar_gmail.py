import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import base64

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/contacts.readonly'
]

def get_credentials():
    """Gets valid user credentials from storage.
    
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    """
    creds = None
    # Always overwrite token.pickle from environment variable if present
    token_b64 = os.environ.get("GOOGLE_TOKEN_PICKLE_B64")
    if token_b64:
        with open("token.pickle", "wb") as f:
            f.write(base64.b64decode(token_b64))
        print("token.pickle written from environment variable (forced overwrite)")
    else:
        print("GOOGLE_TOKEN_PICKLE_B64 not set")
    # Write credentials.json from environment variable if present
    credentials_env = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if credentials_env:
        with open("credentials.json", "w") as f:
            f.write(credentials_env)
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_calendar_service():
    """Returns a Google Calendar service object."""
    creds = get_credentials()
    return build('calendar', 'v3', credentials=creds)

def get_gmail_service():
    """Returns a Gmail service object."""
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def list_calendar_events(max_results=10):
    """Lists the next 10 events on the user's calendar."""
    service = get_calendar_service()
    
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    return events

def send_email(to, subject, message_text):
    """Sends an email using Gmail API."""
    service = get_gmail_service()
    
    message = {
        'raw': base64.urlsafe_b64encode(
            f'To: {to}\r\n'
            f'Subject: {subject}\r\n\r\n'
            f'{message_text}'
            .encode()
        ).decode()
    }
    
    try:
        message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def search_contacts(query, max_results=10):
    service = build('people', 'v1', credentials=get_credentials())
    results = service.people().searchContacts(
        query=query,
        pageSize=max_results,
        readMask='names,emailAddresses,phoneNumbers'
    ).execute()
    return results.get('results', [])

def list_gmail_labels():
    service = get_gmail_service()
    results = service.users().labels().list(userId='me').execute()
    return results.get('labels', [])

def list_messages_by_label(label_id='INBOX', max_results=10):
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=[label_id], maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def get_message_details(message_id):
    service = get_gmail_service()
    msg_detail = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    return msg_detail

def reply_to_message(message_id, reply_text):
    import base64, email
    service = get_gmail_service()
    original = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    headers = original['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
    to = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
    message = email.message.EmailMessage()
    message['To'] = to
    message['Subject'] = 'Re: ' + subject
    message['In-Reply-To'] = message_id
    message.set_content(reply_text)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw, 'threadId': original.get('threadId')}
    sent = service.users().messages().send(userId='me', body=body).execute()
    return sent

def delete_message(message_id):
    service = get_gmail_service()
    service.users().messages().delete(userId='me', id=message_id).execute()
    return {'status': 'deleted', 'id': message_id}

if __name__ == '__main__':
    # Test the connection
    print("Testing Google Calendar connection...")
    events = list_calendar_events()
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event['summary']}")
    
    print("\nTesting Gmail connection...")
    # Uncomment the following line to test sending an email
    # send_email('recipient@example.com', 'Test Subject', 'This is a test email.') 