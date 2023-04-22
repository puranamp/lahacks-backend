import os, re, sys, random
import requests
from dotenv import load_dotenv
import datetime
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_cors import CORS, cross_origin
from models import Vegetable, Product, User
from config import Config
from firebase_admin import credentials, firestore, initialize_app
import pandas as pd

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
    return "Record not found.", 400


@app.route('/getUser', methods=["GET"])
def get_user():
    user_id = request.form["id"]
    doc_ref = users.document(str(user_id)).get()
    if doc_ref.exists:
        return jsonify(doc_ref.to_dict())
    return 'No such user!', 400
        

@app.route('/getUserProducts', methods=["GET"])
def get_user_products():
    user_id = request.form["id"]
    doc_ref = products.document(str(user_id))
    col_ref = doc_ref.collection('unique_products')
    # load in all docs
    docs = col_ref.get()
    mp = {}
    for doc in docs:
        mp[doc.id] = doc.to_dict()
    return jsonify(mp)

@app.route('/addUser', methods=["GET", "POST"])
def add_user():
    if request.method == "GET":
        id = -1
        while id < 0 or id in rand_set:
            id = random.randint(1, 150000)    
        rand_set.add(id)
        user_name = request.form["id"]
        revenue = request.form["revenue"]
        if revenue == None:
            revenue = 0
        location = request.form["location"]
        created_at = datetime.datetime.now()
        user = User(id, user_name, revenue, location, created_at)
        users.document(str(id)).set(user.to_dict())

    return jsonify({user.to_dict()})
    

@app.route('/addProduct', methods=["GET", "POST"])
def add_product():
    if request.method == "GET":
        veggie_id = -1
        while veggie_id < 0 or id in rand_set:
            id = random.randint(1, 150000)
            rand_set.add(id)
            doc_ref = users.document(str(owner_id)).get()
            product = Product(owner_id, veggie_type, date_created, date_ready)
            if doc_ref.exists:
                products.document(str(owner_id)).set({
                    "veggie_id": veggie_id,
                    "product": product.to_dict()
                })
    return jsonify(product.to_dict())

@app.route('/removeProduct', methods=["GET", "POST"])
def remove_product():
    user_id = request.form["id"]
    owner_id = request.form["owner_id"]
    veggie_id = request.form["veggie_id"]
    doc_ref = products.document(str(owner_id))
    col_ref = doc_ref.collection(u'unique_products')
    col_ref.update({str(veggie_id) : firestore.DELETE_FIELD})

def calculate_distance(metrics, comp):
    total = 0
    total += pow(pow((metrics['temperature'] - 273.15) - comp[0], 2), 0.5)
    total += pow(pow(metrics['humidity'] - comp[1], 2), 0.5)
    return total

@app.route('/recommendCrops', methods=["GET", "POST"])
def recommend():
    df = pd.read_csv('./data/data.json')
    user_id = request.form["id"]
    doc_ref = users.document(str(user_id)).get()
    if not doc_ref.exists:
        return "No user found.", 400
    location = doc_ref.to_dict()["location"].split(',')[0]
    temperature = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}, us&APPID=1107f09a2cd574c391617612953ada00").json()
    metrics = {"temperature": temperature["main"]["temp"], "humidity": temperature["main"]["humidity"]}
    # Construct KNN, where distance is the sum of temperature and humidity distance
    distances = [(x, calculate_distance(metrics, (y, z))) for x, y, z in zip(df['label'], df['temperature'], df['humidity'])]
    distances.sort(key=lambda x: x[1])

    num_neighbors = random.randint(4, 7)
    nearest_set, idx, nearest_ordered = set(), 0, []
    while len(nearest_set) != num_neighbors and idx < len(distances):
        if distances[idx][0] not in nearest_set:
            nearest_set.add(distances[idx][0])
            nearest_ordered.append(distances[idx][0])
        idx += 1

    return jsonify({"ranking": nearest_ordered})
    

if __name__ == "__main__":
    app.run(threaded=True, debug=True, port=os.environ.get('PORT'))
