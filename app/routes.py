import os
from flask import Blueprint, request, jsonify, render_template
from .nlu.model import IntentClassifier
from .services.parking_service import get_parking_info
from .services.appointment_service import handle_appointment_message
from .services.session_store import get_session_id, set_session_cookie, get_state, save_state
from .kb.retriever import KnowledgeBase

chatbot_bp = Blueprint('chatbot', __name__)
classifier = IntentClassifier()
kb = KnowledgeBase()

# These intents are better answered by the KB (more precise + sources)
KB_FIRST_INTENTS = {
    "visiting_hours",
    "faq_billing_insurance_cafeteria",
}

# Keywords that indicate "info lookup" (route to KB before random responses)
KB_KEYWORDS = {
    "visit", "visiting", "hours", "icu",
    "pay", "bill", "billing",
    "insurance",
    "cafeteria", "canteen", "food",
    "parking", "park", "directions", "address",
}


@chatbot_bp.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@chatbot_bp.route('/api/get', methods=['POST'])
def get_response():
    sid = get_session_id(request)
    state = get_state(sid)

    def respond(payload: dict):
        resp = jsonify(payload)
        set_session_cookie(resp, sid)
        return resp

    user_msg = (request.json.get('message', '') or '').strip()
    if not user_msg:
        return respond({'response': "Please type a message so I can help."})

    intent, conf = classifier.predict(user_msg)
    msg_lower = user_msg.lower()

    # 1) Service calls for dynamic data
    if intent == 'directions_parking_info':
        return respond({'response': get_parking_info()})

    appointment_related = (
        intent in {"appointment_booking", "appointment_scheduling"}
        or "appointment" in msg_lower
        or "book" in msg_lower
        or "schedule" in msg_lower
        or "my appointment" in msg_lower
        or "next appointment" in msg_lower
        or "appointment details" in msg_lower
    )
    if appointment_related:
        reply, updated_state, _done = handle_appointment_message(user_msg, state)
        save_state(sid, updated_state)
        return respond({'response': reply})

    # 2) If this looks like an "information query", prefer KB retrieval
    looks_like_info_query = any(k in msg_lower for k in KB_KEYWORDS)
    if intent in KB_FIRST_INTENTS or looks_like_info_query or intent == "fallback" or conf < 0.7:
        hits = kb.search(user_msg, top_k=2)

        if hits and hits[0].score >= 0.45:
            best = hits[0]
            show_sources = os.getenv("SHOW_SOURCES", "0") == "1"

            answer = best.excerpt
            if show_sources:
                answer += f"\n\nSource: {best.source} - {best.title}"

            return respond({'response': answer})

    # 3) Otherwise use intent responses (good for greetings/short interactions)
    if intent != 'fallback' and conf >= 0.6:
        return respond({'response': classifier.get_response(intent)})

    # 4) Final fallback
    return respond({
        'response': "Sorry, I'm not sure about that. You can ask about visiting hours, ICU hours, billing, insurance, cafeteria, parking, or appointments."
    })
