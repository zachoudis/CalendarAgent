# Calendar Agent 📅

An intelligent calendar management assistant that uses natural language to create and query Google Calendar events. Built with LLM function calling and structured outputs.

## 🎯 Overview

Calendar Agent is a conversational AI assistant that enables users to manage their Google Calendar through natural language interactions. The system understands user intent, extracts event details, and performs calendar operations seamlessly.

## 🏗️ Architecture

### Single-Agent Design with Function Calling

```
User Message
    ↓
Calendar Manager Agent (with context)
    ↓
Function Tool Selection:
  - event_creator → Create event in Google Calendar
  - event_notifier → Query events for a specific day
    ↓
Google Calendar API
    ↓
Response to User
```

## 🛠️ Key AI/LLM Engineering Techniques

### 1. **Function Calling / Tool Use**
- **Custom function tools** for Google Calendar operations
- **Automatic tool selection** based on user intent
- **Structured tool inputs** using Pydantic models

```python
@function_tool
def event_creator(event: calendarEvent):
    """Create an event in the Google calendar."""
    # Agent automatically calls this when user wants to create an event
```

### 2. **Structured Outputs with Pydantic**
- **Type-safe event models** for calendar operations
- **Automatic validation** of date/time formats
- **Schema enforcement** for API integration

```python
class calendarEvent(BaseModel):
    name: str
    onDate: datetime
    description: str
    duration: int
```

### 3. **Context-Aware Prompting**
- **Current datetime injection** for relative time understanding
- **Timezone-aware processing** (Europe/Berlin)
- **Natural language date parsing** ("tomorrow", "next week", etc.)

```python
now_str = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%dT%H:%M:%S%z")
full_message = f"Current datetime: {now_str}\nUser message: {message}"
```

### 4. **Intent-Based Tool Selection**
- **Agent determines** which tool to call based on user request
- **Missing information handling** - agent asks for clarification
- **Multi-task support** - event creation and querying in one agent

### 5. **OAuth Integration**
- **Google Calendar API authentication** with token management
- **Automatic token refresh** handling
- **Secure credential storage**

### 6. **Error Handling & Validation**
- **Date/time format validation** via Pydantic
- **Missing field detection** before tool execution
- **Graceful API error handling**

## 📦 Technology Stack

- **LLM Framework**: OpenAI Agents SDK (`openai-agents`)
- **Structured Outputs**: Pydantic
- **Calendar API**: Google Calendar API v3
- **Web Framework**: Gradio (ChatInterface)
- **Authentication**: Google OAuth 2.0
- **Timezone Handling**: `zoneinfo`

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key
- Google Calendar API credentials (`credentials.json`)

### Installation

```bash
pip install -r requirements.txt
```

### Setup

1. **Google Calendar API Setup**:
   - Create a project in Google Cloud Console
   - Enable Google Calendar API
   - Download OAuth 2.0 credentials as `credentials.json`

2. **Environment Variables**:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   # Optional: OpenRouter support
   OPENROUTER_API_KEY=your_openrouter_key
   OPENROUTER_API_BASE=your_openrouter_base_url
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```
   First run will prompt for Google OAuth authentication.

## 💡 Usage Examples

- **Create Event**: "Schedule a meeting tomorrow at 2pm for 1 hour about project planning"
- **Query Events**: "What do I have tomorrow?" or "Show me my events for next Friday"
- **Natural Language**: The agent understands relative dates, durations, and event details

## 🎓 LLM Engineering Best Practices Demonstrated

- ✅ **Function Calling**: Seamless integration of external APIs via tools
- ✅ **Structured Data**: Pydantic models ensure type safety and validation
- ✅ **Context Injection**: Current datetime for relative time understanding
- ✅ **Intent Recognition**: Agent determines appropriate actions from natural language
- ✅ **Error Prevention**: Validation before API calls
- ✅ **OAuth Handling**: Secure authentication flow management
- ✅ **Timezone Awareness**: Proper datetime handling across timezones

## 🔍 Technical Highlights

### Natural Language to Structured Data
The agent extracts structured information from conversational input:
- Event name, date/time, description, duration
- Handles missing information by asking clarifying questions
- Validates data before executing calendar operations

### Multi-Task Agent
Single agent handles multiple operations:
- Event creation with automatic tool calling
- Event querying with date extraction
- Context-aware responses based on current time

### Production-Ready Features
- Token refresh handling for long-running sessions
- Error handling for API failures
- Timezone-aware datetime processing
- Clean separation between agent logic and API integration

## 📝 Features

- ✅ Natural language event creation
- ✅ Event querying by date
- ✅ Relative date understanding ("tomorrow", "next week")
- ✅ Automatic duration calculation
- ✅ Google Calendar integration
- ✅ Conversational chat interface

## 👤 Author

Built as a portfolio project showcasing expertise in:
- LLM function calling and tool use
- Structured outputs with Pydantic
- Natural language understanding
- API integration patterns
- Production-ready AI applications

---

**Built with ❤️ for LLM Engineering**
