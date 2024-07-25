from datetime import datetime
import os
import uuid
from flask import Blueprint, jsonify, request
from models import db, DownloadLink, Product

import stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

checkout_bp = Blueprint(name='checkout', import_name=__name__)
@checkout_bp.route('/create-checkout-session/<int:product_id>', methods=['POST'])
def create_checkout_session(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify(error='Product not found'), 404

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
        return jsonify({'id': checkout_session.id})
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
