from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import requests
import os
from ..forms import ReviewForm
import boto3
import json
from decimal import Decimal
from ..models import Review

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
LAMBDA_API_URL_FIND = os.environ.get('LAMBDA_API_URL_FIND')
LAMBDA_API_URL_REVIEW = os.environ.get('LAMBDA_API_URL_REVIEW')

places = Blueprint('places', __name__)


@places.route('/places')
def places_home():
    return render_template('places_test.html', api_key=GOOGLE_API_KEY)

@places.route('/places/search', methods=['POST'])
def search_place():
    data = request.get_json()
    address = data.get('address', '').strip()

    if not address:
        return jsonify({"error": "Missing address"}), 400

    try:
        # Call Lambda via API Gateway
        resp = requests.post(
            f"{LAMBDA_API_URL_FIND}find_places", 
            json={"reference": address},
            timeout=10
        )
        resp.raise_for_status()  # raise exception for HTTP errors

        # Return the Lambda response directly
        return jsonify(resp.json())

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to call Lambda: {str(e)}"}), 500


@places.route('/places/review', methods=['POST'])
@login_required
def review_place():
    data = request.get_json()
    place_id = data.get('place_id')
    rating = data.get('rating')
    comment = data.get('comment')

    # Validate input
    if not all([place_id, rating, comment]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except ValueError:
        return jsonify({"error": "Invalid rating value"}), 400

    # Prepare review data
    review_data = {
        "username": current_user.username,
        "place_id": place_id,
        "rating": rating,
        "comment": comment
    }

    try:
        # Call Lambda via API Gateway to submit review
        resp = requests.post(
            f"{LAMBDA_API_URL_REVIEW}submit_review", 
            json=review_data,
            timeout=10
        )
        resp.raise_for_status()  # raise exception for HTTP errors

        return jsonify({"message": "Review submitted successfully!"}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to submit review: {str(e)}"}), 500
