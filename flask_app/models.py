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
    notes = db.StringField(required=False)
    start_date = db.DateTimeField(required=True)
    end_date = db.DateTimeField(required=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id} by {self.user.username}>"
    
    
# class PeriodLog(Log):
#     flow_intensity = db.StringField(required=True, choices=['light', 'medium', 'heavy'])
#     symptoms = db.ListField(db.StringField(), required=False)
#     mood = db.StringField(required=False)
#     pain_level = db.IntField(min_value=0, max_value=10, required=False)
#     medication_taken = db.ListField(db.StringField(), required=False)
    
# class OvulationLog(Log):
#     ovulation_test_result = db.StringField(required=False, choices=['positive', 'negative', 'not_taken'])
#     symptoms = db.ListField(db.StringField(), required=False)
#     mood = db.StringField(required=False)
    
# class LabLog(Log):
#     test_name = db.StringField(required=True)
#     results_summary = db.StringField(required=False)
#     detailed_report = db.FileField(required=False)
#     tests = db.ListField(db.ReferenceField('LabTest'), required=False)
    
# class MedicationLog(Log):
#     medication_name = db.StringField(required=True)
#     dosage = db.StringField(required=True)
#     frequency = db.StringField(required=True)
#     notes = db.StringField(required=False)
    
# class TemperatureLog(Log):
#     temperature = db.FloatField(required=True)
#     time_recorded = db.DateTimeField(default=datetime.utcnow, required=True)
#     notes = db.StringField(required=False)