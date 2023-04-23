import os, re, sys, random, json
import requests
from dotenv import load_dotenv
import datetime
from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_cors import CORS, cross_origin
from models import Vegetable, Product, User, Transaction
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
transactions = db.collection("transactions")
hashes = db.collection("hashes")
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
        ref = doc_ref.to_dict()
        location = ref["location"]
        weather_data = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}, us&APPID=1107f09a2cd574c391617612953ada00").json()
        res = {
            "id": user_id,
            "name": ref["name"],
            "coords": {
                "latitude": weather_data["coord"]["lat"],
                "longitude": weather_data["coord"]["lon"]
            },
            "sales": [],
            "receipts": [],
            "rating": 3.14159265
        }
        # Sales -> User is the Seller
        # Receipts -> User is the Buyer
        docs = transactions.stream()
        for doc in docs:
            if user_id == doc.get('buyer'):
                res["receipts"].append(doc.to_dict())
            elif user_id == doc.get('seller'):
                res["sales"].append(doc.to_dict())
        
        return res
    return 'No such user!', 400

@app.route('/transact', methods=["GET", "POST"])
def transact():
    if request.method == "POST":
        id = request.form["id"]
        buyer = request.form["buyer"]
        seller = request.form["seller"]
        crop = request.form["product"]
        amt = request.form["amt"]
        price = request.form["price"]
        transaction = Transaction(buyer, seller, crop, amt, price)
        transactions.document(str(id)).set(transaction.to_dict())
        hash_string = "/verify/" + str(hash(json.dumps(transaction.to_dict())))
        hashes.document(hash_string[8:]).set({
            "active": True,
            "transaction_id": id
        })
    return hash_string

@app.route('/verify/<hash_string>')
def verify(hash_string):
    doc_ref = hashes.document(hash_string)
    try:
        real_doc = doc_ref.get().to_dict()
        if real_doc["active"]:
            transaction_doc = transactions.document(real_doc["transaction_id"])
            transaction_doc.update({
                "finished": True
            })
            doc_ref.delete()
    except:
        return "Invalid Hash Token", 400
    
    return "Success!", 200

@app.route('/getVegetable', methods=["GET"])
def get_veggie():
    veggie_name = request.form["name"]
    doc_ref = vegetables.document(veggie_name).get()
    return jsonify(doc_ref.to_dict())

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
    """Basically selling the plant"""
    if request.method == "POST":
        owner_id = request.form["owner_id"]
        veggie_id = request.form["veggie_id"]
        doc_ref = products.document(str(owner_id))
        col_ref = doc_ref.collection(u'unique_products')
        try:
            if col_ref.document(str(veggie_id)).get().to_dict()["ready_for_sale"]:
                col_ref.document(str(veggie_id)).delete()
            else:
                return "Not ready to be sold yet!", 200
        except:
            return "Bad Request", 400
    return "Successful Deletion!", 200

@app.route('/startSale', methods=["POST"])
def start_sale():
    user_id = request.form["id"]
    veggie_id = request.form["veggie_id"]
    doc_ref = products.document(str(user_id))
    col_ref = doc_ref.collection(u'unique_products')
    ref = col_ref.document(str(veggie_id))
    ref.update({
        'ready_for_sale': True
    })
    return ref.get().to_dict()

def calculate_distance(metrics, comp):
    total = 0
    total += pow(pow((metrics['temperature'] - 273.15) - comp[0], 2), 0.5)
    total += pow(pow(metrics['humidity'] - comp[1], 2), 0.5)
    return total

@app.route('/recommendCrops', methods=["GET", "POST"])
def recommend():
    df = pd.read_csv('./data/cropdata.csv')
    discarded_foods = ['Mung Bean', 'Millet', 'Lentil', 'Jute', 'Ground Nut', 'Rubber', 'Tobacco', 'Kidney Beans', 'Moth Beans', 'Black gram', 'Adzuki Beans', 'Pigeon Peas', 'Muskmelon']
    df = df[df.label.isin(discarded_foods) == False]
    discarded_foods = set(discarded_foods)
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
        if distances[idx][0] not in nearest_set and distances[idx][0] not in discarded_foods:
            nearest_set.add(distances[idx][0])
            nearest_ordered.append(distances[idx][0].capitalize())
        idx += 1
    try:
        res = {}
        for element in nearest_ordered:
            docs_ref = vegetables.document(element.capitalize()).get().to_dict()
            res[element] = {}
            if docs_ref['temperature'] > 30:
                res[element]["climate"] = "Warm"
            elif docs_ref['temperature'] > 20:
                res[element]["climate"] = "Temperate"
            else:
                res[element]["climate"] = "Cool"
            if docs_ref['difficulty'] > 4:
                res[element]["experience"] = "Expert"
            elif docs_ref['difficulty'] > 2:
                res[element]["experience"] = "Intermediate"
            else:
                res[element]["experience"] = "Beginner"
            humidity = temperature["main"]["humidity"]
            if humidity >= 65:
                res[element]["humidity"] = "High"
            elif humidity >= 55:
                res[element]["humidity"] = "Moderate"
            else:
                res[element]["humidity"] = "Low"
            clouds = temperature["clouds"]["all"]
            if clouds >= 85:
                res[element]["clouds"] = "Overcast Clouds"
            elif clouds >= 50:
                res[element]["clouds"] = "Broken Clouds"
            elif clouds >= 25:
                res[element]["clouds"] = "Scattered Clouds"
            else:
                res[element]["clouds"] = "Few Clouds"
    except:
        return "Bad Request", 400
    return jsonify(res)

@app.route('/closestCity', methods=["GET"])
def get_closest_city():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    res = requests.get(f"http://api.openweathermap.org/data/2.5/find?lat={latitude}&lon={longitude}&cnt=1&APPID=1107f09a2cd574c391617612953ada00").json()
    if res["cod"] == "404":
        return jsonify({})
    return jsonify({"city": res["list"][0]["name"]})

if __name__ == "__main__":
    app.run(threaded=True, debug=True, host="0.0.0.0", port=os.environ.get('PORT'))
