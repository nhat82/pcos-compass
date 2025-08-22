from datetime import datetime
from database import db
from constants import *

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Event {self.type} {self.start_date}>'

class Period(Event): 
    __tablename__ = "periods"
    
    id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    flow = db.Column(db.Enum(FlowType), nullable=True)
    
    __mapper_args__ = {
        "polymorphic_identity": EventType.PERIOD
    }
    
    def to_dict(self):
        base = super().to_dict()
        base["flow"] = self.flow.name if self.flow else None
        return base


class Ovulation(Event): 
    __tablename__ = "ovulations"
    
    id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    
    __mapper_args__ = {
        "polymorphic_identity": EventType.OVULATION
    }
    
    def to_dict(self):
        base = super().to_dict()
        base["confirmed"] = self.confirmed
        return base

class Note(Event): 
    __tablename__ = "notes"
    
    id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    
    __mapper_args__ = {
        "polymorphic_identity": EventType.NOTE
    }
    
    def to_dict(self):
        return super().to_dict()
