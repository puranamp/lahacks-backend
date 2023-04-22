import os, re, sys, random
from dotenv import load_dotenv
import datetime
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



# @app.route('/addUser', methods=["GET", "POST"])
def add_user(user_name: str, revenue: int, location, created_at):
    id = -1
    while id < 0 or id in rand_set:
        id = random.randint(1, 150000)    
    rand_set.add(id)
    user = User(id, user_name, revenue, location, created_at)
    users.document(str(id)).set(user.to_dict())
    return id


# @app.route('/addVegetable', methods=["GET", "POST"])
def add_vegetable(name: str, season: str, temperature, soil_type):
    veggie = Vegetable(name, season, season, soil_type)
    vegetables.document(name).set(veggie.to_dict())

# @app.route('/addProduct', methods=["GET", "POST"])
def add_product(owner_id: int, veggie_type: str, date_created, date_ready):
    veggie_id = -1
    while veggie_id < 0 or id in rand_set:
        id = random.randint(1, 150000)
    rand_set.add(id)
    doc_ref = users.document(str(owner_id)).get()
    product = Product(owner_id, veggie_type, date_created, date_ready)
    if doc_ref.exists:
        print("Here")
        products.document(str(owner_id)).set({
            "veggie_id": veggie_id,
            "product": product.to_dict()
        })


if __name__ == "__main__":
    app.run(threaded=True, debug=True, port=os.environ.get('PORT'))
