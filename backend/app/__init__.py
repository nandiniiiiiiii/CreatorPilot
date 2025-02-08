from flask import Flask
from flask_cors import CORS
from .routes import main

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for communication with the frontend
    app.register_blueprint(main)
    return app
