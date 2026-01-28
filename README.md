# Hospital Visitor Chatbot (Flask)

A lightweight hospital visitor assistant chatbot built with Flask and vanilla JavaScript.  
It provides a simple web UI, a JSON API endpoint, intent-based responses (from `intents.json`),
and service hooks for dynamic answers like parking info and appointments.

## Features

- Web UI (sidebar quick actions + chat interface)
- Flask backend with a JSON endpoint: `POST /api/get`
- Intent detection using patterns in `app/nlu/intents.json`
- Service hooks for dynamic replies:
  - Parking info (`app/services/parking_service.py`)
  - Appointment lookup/scheduling (`app/services/appointment_service.py`)
- Basic tests (pytest)
- Docker support

## Project Structure

```text
.
├── app/
│   ├── nlu/
│   │   ├── __init__.py
│   │   ├── intents.json          # Intent patterns + responses (core knowledge)
│   │   └── model.py              # Intent classifier
│   ├── services/
│   │   ├── __init__.py
│   │   ├── appointment_service.py
│   │   └── parking_service.py
│   ├── static/
│   │   ├── chat.js               # Frontend logic (calls /api/get)
│   │   └── style.css             # Styling
│   ├── templates/
│   │   └── index.html            # UI
│   ├── __init__.py               # create_app()
│   ├── __main__.py               # Entry point: python -m app
│   └── routes.py                 # Flask routes + intent routing
├── tests/
│   └── test_routes.py
├── Dockerfile
└── requirements.txt
```

## Requirements

- Python 3.10+ recommended
- Optional: Docker

## Run Locally (Ubuntu / macOS / Linux)

1) Create and activate a virtual environment (example using `~/venvs`):

```bash
python3 -m venv ~/venvs/hospital_chatbot
source ~/venvs/hospital_chatbot/bin/activate
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Run the app:

```bash
python -m app
```

4) Open in your browser:

```text
http://127.0.0.1:5000
```

## Run from VS Code

1) Open this project folder in VS Code.  
2) Open the integrated terminal (Terminal → New Terminal).  
3) Activate your venv and run:

```bash
source ~/venvs/hospital_chatbot/bin/activate
python -m app
```

## Run with Docker

Build and run:

```bash
docker build -t hospital-chatbot .
docker run --rm -p 5000:5000 hospital-chatbot
```

Open:

```text
http://127.0.0.1:5000
```

## API Usage

Endpoint:

- `POST /api/get`

Request body:

```json
{ "message": "Visiting hours" }
```

Response:

```json
{ "response": "..." }
```

## Tests

Install and run:

```bash
pip install pytest
pytest
```

## Customizing Intents & Responses

Edit: `app/nlu/intents.json`

Each intent contains:

- `tag`: identifier
- `patterns`: example phrases that trigger the intent
- `responses`: possible answers

Example:

```json
{
  "tag": "visiting_hours",
  "patterns": ["visiting hours", "when can I visit"],
  "responses": ["Visiting hours are 8 AM to 8 PM daily."]
}
```

## Roadmap

- Add a knowledge base with retrieval and sources
- Improve fallback behavior when confidence is low
- Move locale-dependent constants into a config file
- Add logging and feedback collection
- Add more realistic service integrations
