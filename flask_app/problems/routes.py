from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..models import Log
from datetime import datetime
from ..forms import LogForm

problems = Blueprint("problems", __name__)

@problems.route("/problems")
@login_required
def problems_page():
    form = LogForm()
    return render_template("problems.html", form=form)

@problems.route("/problems/data")
@login_required
def problems_data():
    user_problems = Log.objects(user=current_user)
    events = []
    for log in user_problems:
        events.append({
            "id": str(log.id),
            "title": log.description or log.type,
            "start": log.start_date.isoformat(),
            "end": log.end_date.isoformat() if log.end_date else None,
            "allDay": False,
            "extendedProps": {
                "type": log.type,
                "description": log.description
            }
        })
    return jsonify(events)

@problems.route("/problems", methods=["POST"])
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
            start_date=start_date,
            end_date=end_date
        )
        log.save()
        current_user.problems.append(log)
        current_user.save()
        return jsonify({"success": True, "id": str(log.id)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@problems.route("/problems/<log_id>", methods=["PUT"])
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
        
        log.save()
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@problems.route("/problems/<log_id>", methods=["DELETE"])
@login_required
def delete_log(log_id):
    try:
        log = Log.objects(id=log_id, user=current_user).first()
        if not log:
            return jsonify({"success": False, "error": "Log not found"}), 404
        log.delete()
        # Remove from user's problems list
        current_user.update(pull__problems=log)
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500