"""
Load Sample Data into Firestore Database
"""

from firebase_admin import credentials, firestore, initialize_app
from models import User, Product, Vegetable
import datetime
import random

cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()

vegetables = db.collection("vegetables")
products = db.collection("user_products")
users = db.collection("users")
rand_set = set()


def add_user(user_name: str, revenue: int, location, created_at):
    id = -1
    while id < 0 or id in rand_set:
        id = random.randint(1, 150000)    
    rand_set.add(id)
    user = User(id, user_name, revenue, location, created_at)
    users.document(str(id)).set(user.to_dict())
    return id


def add_vegetable(name: str, season: str, temperature, soil_type):
    veggie = Vegetable(name, season, season, soil_type)
    vegetables.document(name).set(veggie.to_dict())


def add_product(owner_id: int, veggie_type: str, date_created, date_ready):
    veggie_id = -1
    while veggie_id < 0 or veggie_id in rand_set:
        veggie_id = random.randint(1, 150000)
    rand_set.add(veggie_id)
    doc_ref = users.document(str(owner_id)).get()
    product = Product(owner_id, veggie_type, date_created, date_ready)
    if doc_ref.exists:
#        products.document(str(owner_id)).set(product.to_dict())
        products.document(str(owner_id)).collection('unique_products').document(str(veggie_id)).set(product.to_dict())
    
    
def random_date(start_date, end_date):
    rand_date = start_date + (end_date - start_date) * random.random()
    formatted_date = rand_date.strftime("%Y-%m-%d")
    return formatted_date
        
def generate_data():
    names = ["Jared", "Felix", "Emily", "Violet", "Rita", "Floyd", "Tony", "Tom", "Angelina"]
    vegetables = ["Carrot", "Grape", "Tomato", "Cabbage"]
    locations = ["Los Angeles, CA", "San Diego, CA", "Las Vegas, NV", "Phoenix, AZ", "Austin, TX", "New York City, NY", "Seattle, WA", "Chicago, IL"]
    # TODO: load in the informtion about the vegetables
    for i in range(5):
        name = random.choice(names)
        location = random.choice(locations)
        created = datetime.datetime(1945, 1, 1)
        start = datetime.datetime(2018, 1, 1)
        end = datetime.datetime(2023, 1, 1)
        user_id = add_user(name, random.randint(0, 750), location, created)
        for veggie in vegetables:
            # create random start date and end date
            start_date = random_date(start, end)
            end_date = random_date(datetime.datetime.strptime(start_date, '%Y-%m-%d'), end)
            add_product(user_id, veggie, start_date, end_date)


if __name__ == "__main__":
    generate_data()
