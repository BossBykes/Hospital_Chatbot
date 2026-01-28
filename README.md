# Hospital Visitor Chatbot (Flask)

A simple hospital visitor assistant chatbot with:
- Flask backend (`/api/get`)
- lightweight intent matching (intents.json)
- basic services (parking info, appointments)
- minimal frontend UI

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app
