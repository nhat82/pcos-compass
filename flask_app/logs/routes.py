# logs.py routes
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..models import Log
from datetime import datetime
from ..forms import CalendarCreateForm

logs = Blueprint("logs", __name__)

@logs.route("/logs")
@login_required
def logs_page():
    form = CalendarCreateForm()
    return render_template("logs.html", form=form)

@logs.route("/logs/data")
@login_required
def logs_data():
    user_logs = Log.objects(user=current_user)
    events = []
    
    # Check if the request wants treatment names or log types
    # show_treatments is TRUE when the toggle is ON (showing detail)
    show_treatments = request.args.get('show_treatments', 'false').lower() == 'true'
    
    for log in user_logs:
        # Determine the title based on the toggle state
        if show_treatments:
            # 1. TOGGLE ON: Show detailed titles (including treatment name and description)
            if log.type != "Treatment":
                # For non-treatment logs, show Type + Description (as title)
                title = log.type + ": " + log.description if log.description else log.type
            else:
                # For treatment logs, prioritize Treatment Name + Description
                title = log.treatment_name + ": " + log.description if log.description else log.treatment_name
        
        else:
            # 2. TOGGLE OFF: Show concise titles (prioritizing the log type)
            if log.type != "Treatment":
                # For non-treatment logs, prioritize the Type (e.g., "Period")
                title = log.type
            else:
                # For treatment logs, show "Treatment" (Type) + Treatment Name
                title = log.type + ": " + log.treatment_name
                
        
        events.append({
            "id": str(log.id),
            "title": title,
            "start": log.start_date.isoformat(),
            "end": log.end_date.isoformat(),
            "allDay": True,
            "extendedProps": {
                "type": log.type,
                "description": log.description,
                "treatment_name": log.treatment_name
            }
        })
    return jsonify(events)



@logs.route("/logs", methods=["POST"])
@login_required
def create_log():
    try:
        data = request.get_json()
        print("Incoming data:", data)

        # Parse dates
        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date")) if data.get("end_date") else None
        log = Log(
                user=current_user,
                type=data.get("type", "Period"),
                description=data.get("description", ""),
                treatment_name=data.get("treatment_name", ""),
                start_date=start_date,
                end_date=end_date
            )
        log.save()
        current_user.logs.append(log)
        current_user.save()
        return jsonify({"success": True, "id": str(log.id)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@logs.route("/logs/<log_id>", methods=["PUT"])
@login_required
def update_log(log_id):
    try:
        data = request.get_json()
        log = Log.objects(id=log_id, user=current_user).first()
        if not log:
            return jsonify({"success": False, "error": "Log not found"}), 404
        
        # Parse dates if provided
        if data.get("start_date"):
            log.start_date = datetime.fromisoformat(data.get("start_date"))
        if data.get("end_date"):
            log.end_date = datetime.fromisoformat(data.get("end_date"))
        
        # Update other fields
        if "type" in data:
            log.type = data.get("type")
        if "description" in data:
            log.description = data.get("description")
        if "treatment_name" in data:
            log.treatment_name = data.get("treatment_name")
        
        log.save()
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@logs.route("/logs/<log_id>", methods=["DELETE"])
@login_required
def delete_log(log_id):
    try:
        log = Log.objects(id=log_id, user=current_user).first()
        if not log:
            return jsonify({"success": False, "error": "Log not found"}), 404
        log.delete()
        # Remove from user's logs list
        current_user.update(pull__logs=log)
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500