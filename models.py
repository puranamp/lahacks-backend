from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

"""
User:
- Still growing / waiting to be sold
- current plants that they are growing
- ID
- Revenue

Vegetable Table (ID to check all vegetables for a specific user)

Vegetables (Data for Processing):
- Location
- Soil
- All that
"""

class User(db.model):
    __tablename__ = "active_users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    revenue = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime)

    def __init__(self, name, revenue=0):
        self.name = name
        self.revenue = revenue

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return "<User ID: {}, Full Name: {}, Revenue: {}, Time Created: {}>".format(id, name, revenue, created_at)

class Products(db.model):
    __tablename__ = "user_products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey("active_users.id"))
    date_ready = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)

    def __init__(self, owner, date_created, date_ready):
        self.owner = owner
        self.date_created = date_created
        self.date_ready = date_ready

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return "".format()


class Vegetable(db.model):
    __tablename__ = "vegetables"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    season = db.Column(db.String(50))
    temperature = db.Column(db.String(50))
    soil_type = db.Column(db.String(50))

    def __init__(self, name, season, temperature, soil_type):
        self.name = name
        self.season = season
        self.temperature = temperature
        self.soil_type = soil_type

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr(self):
        pass
