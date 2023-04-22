import os, re, sys
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from config import Config

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config) # TODO: add config.py file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, support_credentials=True)

@app.route('/', methods=["GET", "POST"])
def index():
    return "", 200

@app.route('/test')
def test():
    """
    Route for any functionality testing
    """
    pass





if __name__ == "__main__":
    app.run(debug=True, port=3000)
