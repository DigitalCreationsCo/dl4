from datetime import datetime, timedelta
import os
import uuid
from flask import Blueprint, abort, flash, jsonify, redirect, request, session, url_for
from models import User, db, DownloadLink, Product
import stripe

from routes.download import is_valid_url
from s3 import get_signed_url

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

checkout_bp = Blueprint(name='checkout', import_name=__name__)
@checkout_bp.route('/generate_checkout_link/<string:product_id>', methods=['POST'])
def generate_checkout_link(product_id):
    if 'user_id' not in session:
        flash('Please log in to generate a checkout link.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('home.index'))
    # Uncomment this check if you want to restrict downloads to paid users
    # if not user or not user.is_paid:
    #     flash('You need to be a paid user to download products.', 'danger')
    #     return redirect(url_for('home.index'))
    
    token = str(uuid.uuid4())
    expiration = datetime.utcnow() + timedelta(hours=24)
    link = DownloadLink(token=token, user_id=user.id, product_id=product_id, 
                        expiration_date=expiration)
    db.session.add(link)
    db.session.commit()
    
    checkout_url = url_for('checkout.create_checkout_session', token=token, _external=True)
    
    print(f"checkout_url: {checkout_url}")
    if is_valid_url(checkout_url):
        flash(
            f"A Checkout link is generated. It has a one-time use and will expire in 24 hours. "
            f"<a target='_blank' href='{checkout_url}'>Your Checkout Link</a> ",
            # f"<button id='download-link' onclick='copyToClipboard()'>Copy</button>", 
            'success'
        )
    else:
        flash("Invalid download URL", 'error')

    return redirect(url_for('home.index'))

@checkout_bp.route('/<string:token>', methods=['GET'])
def create_checkout_session(token):
    download_link = DownloadLink.query.filter_by(token=token, is_used=False).first_or_404()
    
    if download_link.expiration_date <= datetime.utcnow():
        abort(403, description="Download link has expired")
    
    product = Product.query.get_or_404(download_link.product_id)
    if product.image_url:
            object_key = product.image_url.split('com/')[-1]  # Extract the object key from the S3 URL
            product.image_url = get_signed_url(object_key)

    try:
        # Create a new Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': product.price,  # Amount in cents, e.g., $10.00
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'cancel',
        )
        return checkout_session.url
        # return jsonify({'id': checkout_session.id, 'url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 403

@checkout_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # product_id = session.get('client_reference_id')
            product_id = get_product_id_from_session(session)  # Custom logic to map session to product

            if product_id:
                # Generate a unique token for the download link
                token = str(uuid.uuid4())
                expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1 hour expiry

                # Create a new DownloadLink entry in the database
                download_link = DownloadLink(
                    token=token,
                    user_id=session['customer'], # Assuming customer ID is stored in session
                    product_id=product_id,
                    expiration_date=expiration_date,
                    is_used=False
                )
                db.session.add(download_link)
                db.session.commit()

                # Send the download link (in practice, email or display to user)
                print(f'Download link created: {request.host_url}download/{token}')

    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)}), 400

    return jsonify({'status': 'success'})

def get_product_id_from_session(session):
    # Custom logic to extract product ID from session object
    # This could involve looking up the product based on session details
    # Here we simply return a fixed product ID for demonstration purposes
    return 1  # Replace with actual logic to get product ID
