from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..models import treatment
from datetime import datetime
from ..forms import treatmentForm

treatments = Blueprint("treatments", __name__)

@treatments.route("/treatments")

@treatments.route("/treatments/data")
@login_required
def treatments_data():
    user_treatments = treatment.objects(user=current_user)
    events = []
    for treatment in user_treatments:
        events.append({
            "id": str(treatment.id),
            "title": treatment.description or treatment.type,
            "start": treatment.start_date.isoformat(),
            "end": treatment.end_date.isoformat() if treatment.end_date else None,
            "allDay": False,
            "extendedProps": {
                "type": treatment.type,
                "description": treatment.description
            }
        })
    return jsonify(events)

@treatments.route("/treatments", methods=["POST"])
@login_required
def create_treatment():
    try:
        data = request.get_json()
        print("Incoming data:", data)

        # Parse dates
        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date")) if data.get("end_date") else None

        treatment = treatment(
            user=current_user,
            type=data.get("type", "Period"),
            description=data.get("description", ""),
            start_date=start_date,
            end_date=end_date
        )
        treatment.save()
        current_user.treatments.append(treatment)
        current_user.save()
        return jsonify({"success": True, "id": str(treatment.id)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@treatments.route("/treatments/<treatment_id>", methods=["PUT"])
@login_required
def update_treatment(treatment_id):
    try:
        data = request.get_json()
        treatment = treatment.objects(id=treatment_id, user=current_user).first()
        if not treatment:
            return jsonify({"success": False, "error": "treatment not found"}), 404
        
        # Parse dates if provided
        if data.get("start_date"):
            treatment.start_date = datetime.fromisoformat(data.get("start_date"))
        if data.get("end_date"):
            treatment.end_date = datetime.fromisoformat(data.get("end_date"))
        
        # Update other fields
        if "type" in data:
            treatment.type = data.get("type")
        if "description" in data:
            treatment.description = data.get("description")
        
        treatment.save()
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@treatments.route("/treatments/<treatment_id>", methods=["DELETE"])
@login_required
def delete_treatment(treatment_id):
    try:
        treatment = treatment.objects(id=treatment_id, user=current_user).first()
        if not treatment:
            return jsonify({"success": False, "error": "treatment not found"}), 404
        treatment.delete()
        # Remove from user's treatments list
        current_user.update(pull__treatments=treatment)
        return jsonify({"success": True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500