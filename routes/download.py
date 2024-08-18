from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for, flash, session
from datetime import datetime, timedelta
import uuid
import os
from models import db, DownloadLink, Product, User
from s3 import get_signed_url, s3_client
from botocore.exceptions import ClientError
import re

BUCKET_NAME = os.environ.get('AWS_S3_BUCKET')

download_bp = Blueprint(name='download', import_name=__name__)

def is_valid_url(url):
    # Basic regex for URL validation
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(url_regex, url) is not None

@download_bp.route('/generate_link/<string:product_id>', methods=['POST'])
def generate_link(product_id):
    print(f"session {session}")
    if 'user_id' not in session:
        flash('Please log in to generate a download link.', 'danger')
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
    
    download_url = url_for('download.secure_download', token=token, _external=True)
    
    name = request.args.get('name') or 'Product'
    if is_valid_url(download_url):
        flash(
            f"{name} free download link generated. It has a one-time use and will expire in 24 hours. "
            f"<a target='_blank' href='{download_url}'>Your Download Link</a> ",
            # f"<button id='download-link' onclick='copyToClipboard()'>Copy</button>", 
            'success'
        )
    else:
        flash("Invalid download URL", 'error')
    return redirect(url_for('home.index'))

@download_bp.route('/secure_download/<token>')
def secure_download(token):
    download_link = DownloadLink.query.filter_by(token=token, is_used=False).first_or_404()
    
    if download_link.expiration_date <= datetime.utcnow():
        abort(403, description="Download link has expired")
    
    product = Product.query.get_or_404(download_link.product_id)
    if product.image_url:
            object_key = product.image_url.split('com/')[-1]  # Extract the object key from the S3 URL
            product.image_url = get_signed_url(object_key)
    
    file_urls = product.get_file_urls()
    if not file_urls:
        abort(404, description="Product file not found")
    
    file_url = file_urls[0]  # Assuming you want the first file
    try:
        object_key = file_url.split('com/')[-1]  # Extract the object key from the S3 URL
        signed_url = get_signed_url(object_key)
    except ClientError as e:
        print(f"Error generating signed URL: {e}")
        abort(500, description="Error generating download URL")

    product.clicks += 1
    db.session.commit()

    return render_template('download_page.html', product=product, download_url=signed_url, token=token)

@download_bp.route('/download/<string:token>')
def download_file(token):
    download_link = DownloadLink.query.filter_by(token=token, is_used=False).first_or_404()
    
    if download_link.expiration_date <= datetime.utcnow():
        abort(403, description="Download link has expired")
    
    product = Product.query.get_or_404(download_link.product_id)
    
    file_urls = product.get_file_urls()
    if not file_urls:
        abort(404, description="Product file not found")
    
    file_url = file_urls[0]  # Assuming you want the first file
    if not file_urls:
        abort(404, description="Product file not found")
    
    try:
        object_key = file_url.split('com/')[-1]  # Extract the object key from the S3 URL
        signed_url = get_signed_url(object_key)
    except ClientError as e:
        print(f"Error generating signed URL: {e}")
        abort(500, description="Error generating download URL")

    product.download_count += 1
    download_link.is_used = True
    db.session.commit()

    return redirect(signed_url)