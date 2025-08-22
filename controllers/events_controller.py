# controllers/events_controller.py
from flask import Blueprint, request, jsonify
from models import Event
from database import db
from datetime import datetime
from sqlalchemy import asc, exc
from models.models import *
from collections import defaultdict
from models.models import Event, EventType


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
                    'start': event.start_date.isoformat(),
                    'end': event.end_date.isoformat(),
                    'type': event.type,
                    'description': event.description
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
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
                'type': event.type,
                'description': event.description,
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
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
                'type': event.type,
                'description': event.description
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
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
                'type': event.type,
                'description': event.description
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
    
    

@events_bp.route('/events/cycle-length', methods=['GET'])
def cycle_length():
    try:
        # Fetch all PERIOD events ordered by start_date
        periods = Event.query.filter(Event.type == 'PERIOD').order_by(Event.start_date.asc()).all()

        if len(periods) < 2:
            return jsonify({
                'message': f'Not enough period events to calculate cycle length: this has {len(periods)}',
                'data': []
            })

        # Calculate cycle lengths (days between consecutive period starts)
        cycle_lengths_by_month = {}
        for i in range(1, len(periods)):
            prev_start = periods[i - 1].start_date
            curr_start = periods[i].start_date
            diff_days = (curr_start - prev_start).days

            month_key = curr_start.strftime("%b")  # Only month name, e.g., "Aug"
            cycle_lengths_by_month.setdefault(month_key, []).append(diff_days)

        # Average cycle length per month, sorted Jan → Dec
        months_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        result = []
        for month in months_order:
            if month in cycle_lengths_by_month:
                lengths = cycle_lengths_by_month[month]
                avg_length = round(sum(lengths) / len(lengths))
                result.append({'month': month, 'avg_cycle_length': avg_length})

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
