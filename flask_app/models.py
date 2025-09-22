from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True, min_length=4, max_length=20)
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(required=True)
    logs = db.ListField(db.ReferenceField('Log'))
    
    def get_id(self):
        return self.username
    
    def __repr__(self):
        return f"<User {self.username}>"
    
class Log(db.Document):
    meta = {'allow_inheritance': True}
    user = db.ReferenceField(User, required=True)
    type = db.StringField(required=True, default='PERIOD') 
    description = db.StringField()
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id} by {self.user.username}>"
    
class Place(db.Document):
    name = db.StringField(required=True)
    address = db.StringField(required=True)
    link = db.StringField()
    latitude = db.FloatField()
    longitude = db.FloatField()
    description = db.StringField()
    posted_by = db.ReferenceField(User, required=True)
    average_rating = db.FloatField(default=0.0)
    reviews = db.ListField(db.ReferenceField('Review'))
    
    def get_id(self):
        return self.name
        
    def __repr__(self):
        return f"<{self.name}>"
    
class Review(db.Document):
    place = db.ReferenceField(Place, required=True)
    user = db.ReferenceField(User, required=True)
    rating = db.IntField(min_value=1, max_value=5, required=True)
    comment = db.StringField()
    created_at = db.DateTimeField(required=True)
    
    def __repr__(self):
        return f"<Review {self.id} for {self.place.name} by {self.user.username}>"
    
class Treatment(db.Document):
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=False)
    details = db.StringField()  # e.g., dosage, notes
    effectiveness = db.StringField(
        choices=["improved", "no_change", "worse", "unknown"], default="unknown"
    )
    user = db.ReferenceField(User, required=True)

class Problem(db.Document):
    name = db.StringField(required=True)      # e.g., "acne", "irregular periods"
    severity = db.IntField(min_value=1, max_value=5)  # 1 = mild, 5 = severe
    notes = db.StringField()
    user = db.ReferenceField(User, required=True)