from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from flask_app.constants import INSIGHT_STATUSES

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True, min_length=4, max_length=20)
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(required=True)
    logs = db.ListField(db.ReferenceField('Log'))
    problems = db.ListField(db.ReferenceField('Problem'))
    insights = db.ListField(db.ReferenceField('Insight'))
    
    def get_id(self):
        return self.username
    
    def __repr__(self):
        return f"<User {self.username}>"
    

class Problem(db.Document):
    name = db.StringField(required=True)      # e.g., "Acne", "Hair Loss"
    details = db.StringField() 
    user = db.ReferenceField(('User'), required=True)
    
    def __repr__(self):
        return f"<Problem {self.name} of {self.user.username}>"

class Log(db.Document):
    user = db.ReferenceField(User, required=True)
    type = db.StringField(required=True, default='Period') 
    description = db.StringField()
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=True)
    treatment_name = db.StringField()
    problem = db.ReferenceField(('Problem'), required=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id} by {self.user.username}>"
    
class Treatment(db.Document):
    name = db.StringField(required=True)
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=True)
    details = db.StringField()
    user = db.ReferenceField(User, required=True)
    
    def __repr__(self):
        return f"<Treatment {self.name} for {self.user.name}>"


# class Place(db.Document):
#     name = db.StringField(required=True)
#     address = db.StringField(required=True)
#     link = db.StringField()
#     latitude = db.FloatField()
#     longitude = db.FloatField()
#     description = db.StringField()
#     posted_by = db.ReferenceField(User, required=True)
#     average_rating = db.FloatField(default=0.0)
#     reviews = db.ListField(db.ReferenceField('Review'))
    
#     def get_id(self):
#         return self.name
        
#     def __repr__(self):
#         return f"<{self.name}>"
    
class Review(db.Document):
    place = db.ReferenceField(('Place'), required=True)
    user = db.ReferenceField(('User'), required=True)
    rating = db.IntField(min_value=1, max_value=5, required=True)
    comment = db.StringField()
    created_at = db.DateTimeField(required=True)
    
    def __repr__(self):
        return f"<Review {self.id} for {self.place.name} by {self.user.username}>"

class Insight(db.Document):
    status = db.StringField(choices=INSIGHT_STATUSES, default="NO_CHANGE")
    content = db.StringField(required=True)
    problem = db.ReferenceField(('Problem'), required=True)
    treatment = db.ReferenceField('Treatment', required=True)
    user = db.ReferenceField(('User'), required=True)
    
    def __repr__(self):
        return f"<Insight {self.content} by {self.user.username}>"

