import json
import random

class IntentClassifier:
    def __init__(self):
        with open('app/nlu/intents.json') as f:
            self.intents = json.load(f)['intents']

    def predict(self, text: str):
        text_lower = text.lower()
        for intent in self.intents:
            for pattern in intent['patterns']:
                if pattern.lower() in text_lower:
                    # match by pattern
                    return intent['tag'], 1.0
        return 'fallback', 0.0

    def get_response(self, tag: str):
        for intent in self.intents:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
        return "Sorry, I didn't understand that."  