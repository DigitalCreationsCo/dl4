from flask import Blueprint, abort, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta
import uuid
import os
from models import db, DownloadLink, Product, User
from s3 import get_signed_url, s3_client
from botocore.exceptions import ClientError

BUCKET_NAME = os.environ.get('AWS_S3_BUCKET')

download_bp = Blueprint(name='download', import_name=__name__)
@download_bp.route('/generate_link/<int:product_id>', methods=['POST'])
def generate_link(product_id):
    if 'user_id' not in session:
        flash('Please log in to generate a download link.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    # if not user or not user.is_paid:
    #     flash('You need to be a paid user to download products.', 'danger')
    #     return redirect(url_for('home.index'))
    
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('home.index'))
    
    token = str(uuid.uuid4())
    expiration = datetime.utcnow() + timedelta(hours=24)
    link = DownloadLink(token=token, user_id=user.id, product_id=product_id, 
                        expiration_date=expiration)
    db.session.add(link)
    db.session.commit()
    
    flash(f'Download link generated. It will expire in 24 hours.', 'success')
    return redirect(url_for('download.secure_download', token=token))

@download_bp.route('/secure_download/<token>')
def secure_download(token):
    print(f"token {token}")
    download_link = DownloadLink.query.filter_by(token=token, is_used=False).first()
    
    if download_link and download_link.expiration_date > datetime.utcnow():
        # Mark link as used
        download_link.is_used = True
        db.session.commit()

        # Fetch the product to determine file path
        product = Product.query.get(download_link.product_id)

        if product:
            # Serve the file for download
            file_url = product.get_file_urls()[0]
            if not file_url:
                return jsonify({'error': 'Product file not found'}), 404
            
            try:
                object_key = file_url.split('com/')[-1]  # Extract the object key from the S3 URL
                signed_url = get_signed_url(object_key)
            except ClientError as e:
                print(f"error: {e}")
                abort(500)

            # Log the download
            # log_download(current_user.id, product_id, file_index)
            return signed_url
        else:
            return jsonify({'error': 'Product file not found'}), 404
    else:
        return jsonify({'error': 'Invalid or expired download link'}), 403
    
# def log_download(user_id, product_id, file_index):
#     # Implement download logging here
#     pass