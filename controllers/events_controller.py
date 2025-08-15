from flask import Blueprint, request, jsonify
from database import db

from models.models import * 
from constants import *

events_bp = Blueprint("events", __name__, url_prefix="/events")

@events_bp.route("/", methods=["POST"])
def create_event():
    data = request.get_json()
    event_type = EventType[data["type"]]
    start_date = datetime.fromisoformat(data["start_date"])
    end_date = datetime.fromisoformat(data["end_date"])
    description = data.get("description")

    if event_type == EventType.PERIOD:
        flow = FlowType[data["flow"]] if "flow" in data else None
        new_event = Period(
            start_date=start_date,
            end_date=end_date,
            description=description,
            flow=flow
        )
    elif event_type == EventType.OVULATION:
        confirmed = data.get("confirmed", False)
        new_event = Ovulation(
            start_date=start_date,
            end_date=end_date,
            description=description,
            confirmed=confirmed
        )
    else:
        new_event = Note(
            start_date=start_date,
            end_date=end_date,
            description=description
        )

    db.session.add(new_event)
    db.session.commit()
    return new_event.to_dict(), 201
    


@events_bp.route("/", methods=["GET"])
def get_events():
    events = [event.to_dict() for event in Event.query.all()]
    return {"count": len(events), "events": events}


@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return event.to_dict()


@events_bp.route("/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.json
    
    for key, val in data.items():
        if key != "flow":
            setattr(event, key, val)
        else: 
            event.flow = FlowType[data["flow"]]
        
    db.session.commit()
    return jsonify({"id": event.id, "message": "Event updated"}), 200


@events_bp.route("/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"id": event.id, "message": "Event deleted"}), 200
