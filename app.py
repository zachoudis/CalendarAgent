"""
Calendar Management Agent Application
A Gradio-based chat interface for managing Google Calendar events.
"""

import os
from typing import Dict
from datetime import datetime, timedelta, date
from datetime import time as dt_time
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import gradio as gr

from agents import Agent, Runner, function_tool

# Load environment variables
load_dotenv(override=True)

# Google Calendar configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# Pushover configuration (optional)
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

# Map OpenRouter credentials to OpenAI-compatible env vars
if os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
if os.getenv("OPENROUTER_API_BASE"):
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENROUTER_API_BASE")


# Pydantic Models
class calendarEvent(BaseModel):
    """Model for calendar event creation."""
    name: str = Field(description="The name of the event")
    onDate: datetime = Field(description="The date that the event takes place. The datetime structure should be like this: 2026-02-18T15:00:00+01:00")
    description: str = Field(description="What is this event about. Description of it")
    duration: int = Field(description="For how long this event takes place")


class day(BaseModel):
    """Model for requesting events on a specific day."""
    day: datetime = Field(description="The calendar day that the user is requesting to see all the events that he has on his calendar. The datetime structure should be like this: 2026-02-18T15:00:00+01:00")


# Helper Functions
def get_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def generate_google_calendar_event(event: calendarEvent) -> Dict:
    """Convert calendarEvent model to Google Calendar API format."""
    return {
        "summary": event.name,
        "description": event.description,
        "start": {
            "dateTime": event.onDate.isoformat(),
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "dateTime": (event.onDate + timedelta(minutes=event.duration)).isoformat(),
            "timeZone": "Europe/Berlin",
        },
    }


# Function Tools
@function_tool
def event_creator(event: calendarEvent):
    """Create an event in the Google calendar."""
    body = generate_google_calendar_event(event)
    service = get_calendar_service()
    created_event = service.events().insert(
        calendarId="mbehrends1804@gmail.com", 
        body=body
    ).execute()
    
    return f"Event '{created_event['summary']}' scheduled on {created_event['start']['dateTime']}."


@function_tool
def event_notifier(currentDay: day):
    """Get events for a specific day from Google Calendar."""
    berlin_tz = ZoneInfo("Europe/Berlin")
    requested_date = currentDay.day.date() if isinstance(currentDay.day, datetime) else currentDay.day
    
    # Start and end of day in Berlin timezone (aware datetimes)
    start_of_day = datetime.combine(requested_date, dt_time.min, tzinfo=berlin_tz)
    end_of_day = datetime.combine(requested_date, dt_time.max, tzinfo=berlin_tz)
    
    print(f"Searching events from {start_of_day.isoformat()} to {end_of_day.isoformat()}")
    
    service = get_calendar_service()
    
    events_result = service.events().list(
        calendarId='mbehrends1804@gmail.com',
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        return f"No events found for {requested_date.strftime('%Y-%m-%d')}."
    
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        event_list.append(f"- {summary} at {start}")
    
    return f"Events for {requested_date.strftime('%Y-%m-%d')}:\n" + "\n".join(event_list)


# Agent Setup
tools = [event_creator, event_notifier]

instructions = """You are the assistant of Paris Zachoudis and Meike Behrends, your responsibility is to help them with their work 
and to be a friendly assistant.
Your first task is to add for them events in their calendar when they ask you to. Their shared calendar is a google calendar.
If the user wants to create an event,you MUST call the event_creator tool.

Extract:
- name
- date
- description
- duration

If any required information is missing,
ask the user before calling the tool.

Do NOT respond with text if the user wants to create an event.
Always call the tool.

Your second task is to tell the user the events he has for the day he requested to know about. If the user requests to know what the events or what he has to do for tomorrow
call the event_notifier_tool
Extract:
- date
"""

assistant_agent = Agent(
    name="Calendar Manager",
    instructions=instructions,
    tools=tools,
    model="gpt-4o-mini"
)


# Gradio Interface
async def chat(message, history):
    """Chat function for Gradio interface."""
    now_str = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%dT%H:%M:%S%z")
    full_message = (
        f"Current datetime: {now_str}\n"
        f"User message: {message}"
    )

    result = await Runner.run(assistant_agent, full_message)
    return result.final_output


def main():
    """Main function to launch the Gradio app."""
    demo = gr.ChatInterface(
        fn=chat,
        title="Paris Calendar Organizaaah"
    )
    demo.launch()


if __name__ == "__main__":
    main()
