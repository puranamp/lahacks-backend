import os, re, sys, random
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_cors import CORS, cross_origin
from models import Vegetable, Product, User
from config import Config
from firebase_admin import credentials, firestore, initialize_app


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, support_credentials=True)
cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()

# (Tables)
vegetables = db.collection("vegetables")
products = db.collection("user_products")
users = db.collection("users")
rand_set = set()


@app.route('/', methods=["GET", "POST"])
def index():
    return "", 200

@app.route('/test')
def test():
    """
    Route for any functionality testing
    """
    pass

@app.route('/addUser', methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        id = -1
        while id < 0 or id in rand_set:
            id = random.randint(1, 150000)
        rand_set.add(id)
        name = request.form["name"]
        revenue = 0
        if "revenue" in request.form:
            revenue = request.form["revenue"]
        location = request.form["location"]
        created_at = datetime.now().date().strftime('%d-%m-%y')
        user = User(id, name, revenue, location, created_at)
        users.document(str(id)).set(user.to_dict())
    return jsonify(user.to_dict())

@app.route('/addVegetable', methods=["GET", "POST"])
def add_vegetable():
    if request.method == "POST":
        name = request.form["name"]
        season = request.form["season"]
        temperature = request.form["temperature"]
        soil_type = request.form["soil_type"]
        veggie = Vegetable(name, season, season, soil_type)
        vegetables.document(name).set(veggie.to_dict())
    return jsonify(veggie.to_dict())

@app.route('/addProduct', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        owner_id = request.form["owner_id"]
        type = request.form["type"]
        date_created = request.form["date_created"]
        date_ready = request.form["date_ready"]
        # first query and see if the owner exists, only then add
        query = users.where(u'id', u'==', owner_id).stream()
        product = Product(owner_id, type, date_created, date_ready)
        if len(query) != 0:
            products.document(type).set(product.to_dict())
            return jsonify(product.to_dict())
    return jsonify({})

if __name__ == "__main__":
    app.run(threaded=True, debug=True, port=os.environ.get('PORT'))
