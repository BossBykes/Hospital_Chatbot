from pathlib import Path
from flask import Flask
from .config import BaseConfig

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(BaseConfig)

    db_path = Path(app.config["DATABASE_PATH"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    from .routes import chatbot_bp
    app.register_blueprint(chatbot_bp)

    return app
