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
