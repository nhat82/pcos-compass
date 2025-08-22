# controllers/events_controller.py
from flask import Blueprint, request, jsonify
from models import Event
from database import db
from datetime import datetime
from sqlalchemy import exc
from models.models import *

events_bp = Blueprint('events', __name__)

@events_bp.route('/events/', methods=['GET', 'POST'])
def events():
    if request.method == 'GET':
        try:
            events = Event.query.all()
            events_data = []
            for event in events:
                events_data.append({
                    'id': event.id,
                    # 'title': event.description or event.type,
                    'start': event.start_date.isoformat(),
                    'end': event.end_date.isoformat(),
                    'extendedProps': {
                        'type': event.type,
                        'description': event.description
                    },
                    # 'allDay': True
                })
            return jsonify(events_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('type') or not data.get('start_date') or not data.get('end_date'):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Parse dates
            start_date = parse_date(data['start_date'])
            end_date = parse_date(data['end_date'])
            
            if not start_date or not end_date:
                return jsonify({'error': 'Invalid date format'}), 400
            
            # Create event
            event = Event(
                type=data['type'],
                description=data.get('description'),
                start_date=start_date,
                end_date=end_date
            )
            
            db.session.add(event)
            db.session.commit()
            
            return jsonify({
                'id': event.id,
                'type': event.type,
                'description': event.description,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat()
            }), 201
            
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Database error: ' + str(e)}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@events_bp.route('/events/<int:event_id>', methods=['GET', 'PUT'])
def event(event_id):
    try:
        event = Event.query.get(event_id)
        
        # Check if event exists
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'id': event.id,
                'type': event.type,
                'description': event.description,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat()
            })
            
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Validate required fields
            if not data.get('type') or not data.get('start_date') or not data.get('end_date'):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Parse dates
            start_date = parse_date(data['start_date'])
            end_date = parse_date(data['end_date'])
            
            if not start_date or not end_date:
                return jsonify({'error': 'Invalid date format'}), 400
            
            # Update event
            event.type = data['type']
            event.description = data.get('description')
            event.start_date = start_date
            event.end_date = end_date
            
            db.session.commit()
            
            return jsonify({
                'id': event.id,
                'type': event.type,
                'description': event.description,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat()
            })
            
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_date(date_string):
    """Parse date string from various formats"""
    try:
        # Try ISO format first
        if date_string.endswith('Z'):
            date_string = date_string.replace('Z', '+00:00')
        return datetime.fromisoformat(date_string)
    except ValueError:
        try:
            # Try format without timezone
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                return datetime.strptime(date_string, '%Y-%m-%d')
            except ValueError:
                return None

# def is_all_day_event(start_date, end_date):
#     """Check if event is all-day (starts and ends at midnight)"""
#     return (start_date.time() == end_date.time() == datetime.min.time() and
#             (end_date - start_date).days >= 1)
    
    
@events_bp.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Delete from related tables based on event type
        if event.type == 'PERIOD':
            # Use 'id' to filter, not 'event_id'
            periods_deleted = Period.query.filter_by(id=event_id).delete()
            print(f"Deleted {periods_deleted} period records for event {event_id}")
        
        elif event.type == 'NOTE':
            # Use 'id' to filter
            notes_deleted = Note.query.filter_by(id=event_id).delete()
            print(f"Deleted {notes_deleted} note records for event {event_id}")
            
        elif event.type == 'OVULATION':
            # Use 'id' to filter
            ovulation_deleted = Ovulation.query.filter_by(id=event_id).delete()
            print(f"Deleted {ovulation_deleted} ovulation records for event {event_id}")
        
        # Then delete the event itself
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event deleted successfully',
            'event_type': event.type,
            'deleted_event_id': event_id
        }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500