from flask import Blueprint, request, jsonify, render_template
from .nlu.model import IntentClassifier
from .services.parking_service import get_parking_info
from .services.appointment_service import lookup_appointment, schedule_appointment

chatbot_bp = Blueprint('chatbot', __name__)
classifier = IntentClassifier()

@chatbot_bp.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@chatbot_bp.route('/api/get', methods=['POST'])
def get_response():
    user_msg = request.json.get('message', '')
    intent, _ = classifier.predict(user_msg)

    # Hook service calls for dynamic data
    if intent == 'directions_parking_info':
        resp = get_parking_info()
    elif intent == 'appointment_booking':
        # Example: just lookup next appointment
        resp = lookup_appointment(user_msg)
    elif intent == 'appointment_scheduling':
        resp = schedule_appointment(user_msg)
    else:
        resp = classifier.get_response(intent)

    return jsonify({'response': resp})