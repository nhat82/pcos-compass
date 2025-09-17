from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import * 
from ..models import *

places = Blueprint('places', __name__)

''' Place Management Views '''

@places.route('/places', methods=['GET', 'POST'])
@login_required
def list_places():
    all_places = Place.objects()
    form = PlaceForm()
    if form.validate_on_submit():
        new_place = Place(
            name=form.name.data,
            address=form.address.data,
            link = form.link.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            posted_by=current_user._get_current_object()
        )
        new_place.save()
        flash('Place added successfully!', 'success')
    return render_template('places.html', places=all_places, form=form)


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