from flask import Blueprint, redirect, render_template, request, flash, current_app, url_for, session
from werkzeug.utils import secure_filename
import os
from models import db, Product
from routes.home import login_required
from s3 import delete_file_from_s3, upload_file_to_s3

product_bp = Blueprint(name='product', import_name=__name__)

@product_bp.route('/upload_product', methods=['GET', 'POST'])
@login_required
def upload_product():
    if request.method == 'POST':

        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to upload a product', 'danger')
            return redirect(url_for('home.index'))
        
        name=request.form['product_name']
        description=request.form['product_description']
        price=request.form['product_price']
        image=request.files['product_image']

        if 'product_file' in request.files:
            file = request.files['product_file']
            if file.filename != '':
                product_name = secure_filename(name)
                filename = secure_filename(file.filename)

                if image:
                    image_name = secure_filename(image.filename)
                    image_url = upload_file_to_s3(image, f"products/{product_name}/{image_name}", ACL='public-read')
                else:
                    image_url = None

                file_url = upload_file_to_s3(file, f"products/{product_name}/{filename}")
                if file_url:
                    product = Product(name=name, description=description, price=price, user_id=user_id, file_urls=file_url, image_url=image_url, is_folder=False)
                    db.session.add(product)
                    db.session.commit()
                    flash('Product uploaded successfully!', 'success')
                else:
                    flash('Failed to upload file to S3', 'danger')
            else:
                flash('No file selected', 'danger')     
                return render_template('home.html')

        elif 'product_folder' in request.files:
            # files = request.files.getlist('product_folder')
            # if files:
            #     folder_name = secure_filename(request.form['product_name'])
            #     folder_urls = []
            #     for file in files:
            #         if file.filename != '':
            #             filename = secure_filename(file.filename)
            #             object_name = f"products/{user_id}/{folder_name}/{filename}"
            #             file_url = upload_file_to_s3(file, object_name)
            #             if file_url:
            #                 folder_urls.append(file_url)
            #             else:
            #                 flash(f'Failed to upload {filename} to S3', 'warning')
            #     if folder_urls:
            #         product = Product(name=name, description=description, price=price, user_id=user_id, file_urls=folder_urls, image_url=image_url, is_folder=True)
            #         db.session.add(product)
            #         db.session.commit()
            #         flash('Product folder uploaded successfully!', 'success')
            #     else:
            #         flash('Failed to upload any files to S3', 'danger')
            # else:
            #     flash('No folder selected', 'danger')

            # os.walk to get all files in a folder https://gist.github.com/feelinc/d1f541af4f31d09a2ec3
            folder = request.files['product_folder']
            if folder.filename != '':
                folder_name = secure_filename(folder.filename)
                folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
                folder.save(folder_path)
                folder_urls = []
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        object_name = f"products/{user_id}/{folder_name}/{file}"
                        file_url = upload_file_to_s3(file_path, object_name)
                        if file_url:
                            folder_urls.append(file_url)
                        else:
                            flash(f'Failed to upload {file} to S3', 'warning')
                if folder_urls:
                    product = Product(name=name, description=description, price=price, user_id=user_id, file_urls=folder_urls, image_url=image_url, is_folder=True)
                    db.session.add(product)
                    db.session.commit()
                    flash('Product folder uploaded successfully!', 'success')
                else:
                    flash('Failed to upload any files to S3', 'danger')
            else:
                flash('No folder selected', 'danger')

        else:
            flash('No file or folder uploaded', 'danger')
        return redirect(url_for('home.index'))
    return render_template('home.html')

@product_bp.route('/delete_product/<string:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.user_id != session.get('user_id'):
        return "Unauthorized", 403
    
    if product.image_url:
        object_name = product.image_url.split('/')[-1]
        delete_file_from_s3(object_name)
    
    for file in product.get_file_urls():  # Replace `files` with your actual relationship or field
        object_name = file.split('/')[-1]
        delete_file_from_s3(object_name)
        
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('home.index'))