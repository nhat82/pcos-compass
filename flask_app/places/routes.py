from flask import Blueprint, render_template, redirect, url_for, flash, request
import requests
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import * 
from ..models import *
from ..config import GOOGLE_API_KEY
import folium

places = Blueprint('places', __name__)

''' Place Management Views '''

@places.route('/places', methods=['GET', 'POST'])
@login_required
def list_places():
    # need to limit this to their local area 
    all_places = Place.objects()
    
    search_form = SearchPlaceForm()
    add_form = AddPlaceForm()
    
    existing_place = None
    
    if search_form.validate_on_submit():
        query = search_form.search_query.data
        # needs to standardize the text format
        existing_place = Place.objects(name=query).first()

        if existing_place:
            flash(f"Found a place matching your search: {existing_place.name}", "success")
        else:
            # Get place details from Google (after user selects suggestion)
            # place_details = get_place_details_from_google(query)
            # if place_details:
            #     place = Place(
            #         name=place_details["name"],
            #         address=place_details["address"],
            #         link=f"https://www.google.com/maps/place/?q=place_id:{place_details['place_id']}",
            #         latitude=place_details["lat"],
            #         longitude=place_details["lng"],
            #         posted_by=current_user._get_current_object()
            #     )
            #     place.save()
            #     flash('Place added successfully!', 'success')
            # else:
                flash(f"No place found with the name '{query}'.", "error")
                
    if all_places:
        avg_lat = sum(p.latitude for p in all_places) / len(all_places)
        avg_lon = sum(p.longitude for p in all_places) / len(all_places)
        m = folium.Map(location=[32.07148197,34.7876717], zoom_start=14, control_scale=True) 
    else:
        m = folium.Map(location=[32.07148197,34.7876717], zoom_start=14, control_scale=True) 

    # Add a marker for each place
    for place in all_places:
        folium.Marker(
            location=[place.latitude, place.longitude],
            tooltip=place.name,
            popup=f"<b>{place.name}</b><br>{place.description}"
        ).add_to(m)

    # Save the map as an HTML file
    map_html = m._repr_html_()
    
    return render_template(
        'places.html',
        places=all_places,
        search_form=search_form, 
        existing_place = existing_place, 
        map_html=map_html
    )


# helper functions
"""Call Google Places Autocomplete + Details to get place info"""

# def get_place_details_from_google(query):    
#     # Autocomplete to get place_id
#     autocomplete_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
#     params = {"input": query, "key": GOOGLE_API_KEY}
#     r = requests.get(autocomplete_url, params=params).json()
#     predictions = r.get("predictions")
#     if not predictions:
#         return None

#     # Take the first prediction (or let user select in frontend)
#     place_id = predictions[0]["place_id"]

#     # Step 2: Get place details
#     details_url = "https://maps.googleapis.com/maps/api/place/details/json"
#     params = {"place_id": place_id, "key": GOOGLE_API_KEY, "fields": "name,geometry,formatted_address"}
#     r = requests.get(details_url, params=params).json()
#     result = r.get("result")
#     if not result:
#         return None

#     return {
#         "name": result.get("name"),
#         "address": result.get("formatted_address"),
#         "lat": result["geometry"]["location"]["lat"],
#         "lng": result["geometry"]["location"]["lng"],
#         "place_id": place_id
#     }



@places.route('/places/<place_id>', methods=['GET', 'POST'])
@login_required
def place_detail(place_id):
    place = Place.objects(id=place_id).first()
    if not place:
        flash('Place not found.', 'danger')
        return redirect(url_for('places.list_places'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        new_review = Review(
            place=place,
            user=current_user._get_current_object(),
            rating=form.rating.data,
            comment=form.comment.data,
            created_at=datetime.now()
        )
        new_review.save()
        place.reviews.append(new_review)
        # Update average rating
        total_rating = sum(review.rating for review in place.reviews)
        place.average_rating = total_rating / len(place.reviews)
        place.save()
        
        flash('Review added successfully!', 'success')
    return render_template('place_detail.html', place=place, form=form)
    

@places.route('/places/<place_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(place_id):
    place = Place.objects(id=place_id).first()
    if not place:
        flash('Place not found.', 'danger')
        return redirect(url_for('places.list_places'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        new_review = Review(
            place=place,
            user=current_user._get_current_object(),
            rating=form.rating.data,
            comment=form.comment.data,
            created_at=datetime.datetime.now()
        )
        new_review.save()
        place.reviews.append(new_review)
        # Update average rating
        total_rating = sum(review.rating for review in place.reviews)
        place.average_rating = total_rating / len(place.reviews)
        place.save()
        
        flash('Review added successfully!', 'success')
        return redirect(url_for('places.place_detail', place_id=place_id))
    
    return render_template('add_review.html', form=form, place=place)