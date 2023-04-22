class User(object):
    def __init__(self, id, name, revenue=0, location="", created_at=None):
        self.id = id
        self.name = name
        self.revenue = revenue
        self.location = location
        self.created_at = created_at

    def to_dict(self):
        return {"name": self.name, "revenue": self.revenue, "location": self.location, "created_at": self.created_at}
        
    def __repr__(self):
        return "<User ID: {}, Full Name: {}, Revenue: {}, Time Created: {}>".format(id, name, revenue, created_at)

class Product(object):
    def __init__(self, owner_id, type, date_created, date_ready):
        self.owner_id = owner_id
        self.type = type
        self.date_created = date_created
        self.date_ready = date_ready

    def to_dict(self):
        return {"owner": self.owner, "type": self.type, "date_created": self.date_created, "date_ready": self.date_ready}
    
    def __repr__(self):
        return "".format()


class Vegetable(object):
    def __init__(self, name, season, temperature, soil_type):
        self.name = name
        self.season = season
        self.temperature = temperature
        self.soil_type = soil_type

    def to_dict(self):
        return {"name": self.name, "season": self.season, "temperature": self.temperature, "soil_type": self.soil_type}
        
    def __repr(self):
        pass
