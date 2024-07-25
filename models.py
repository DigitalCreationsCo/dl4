from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String, nullable=True)
    file_urls = db.Column(db.Text, nullable=False)  # Changed from file_path to file_urls
    is_folder = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, description, price, user_id, file_urls, image_url=None, is_folder=False):
        self.name = name
        self.description = description
        self.price = price
        self.user_id = user_id
        self.file_urls = file_urls if isinstance(file_urls, str) else ','.join(file_urls)
        self.image_url = image_url
        self.is_folder = is_folder

    def get_file_urls(self):
        return self.file_urls.split(',') if self.file_urls else []

    def set_file_urls(self, urls):
        self.file_urls = ','.join(urls) if urls else None

    def __repr__(self):
        return f'<Product {self.name}>'

class DownloadLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
