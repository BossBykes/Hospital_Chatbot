from flask import Flask

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    from .routes import chatbot_bp
    app.register_blueprint(chatbot_bp)

    return app