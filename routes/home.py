from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import Product
from s3 import get_signed_url

home_bp = Blueprint('home',__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@home_bp.route('/success')
def success():
    # Flash a success message
    flash("Your action was successful!", "success")
    # Redirect to the index page
    return redirect(url_for('home.index'))

@home_bp.route('/error')
def error():
    # Flash an error message
    flash("An error occurred. Please try again.", "error")
    # Redirect to the index page
    return redirect(url_for('home.index'))

@home_bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))  
    
    products = Product.query.filter_by(user_id=user_id).all()
    # get signed url for each product image
    for product in products:
        if product.image_url:
            object_key = product.image_url.split('com/')[-1]  # Extract the object key from the S3 URL
            product.image_url = get_signed_url(object_key)
    return render_template('home.html', products=products)
    