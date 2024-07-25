from flask import Flask
from config import Config
from models import db
from routes.home import home_bp
from routes.auth import auth_bp
from routes.checkout import checkout_bp
from routes.download import download_bp
from routes.product import product_bp
from admin.views import admin, admin_required

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(download_bp)
app.register_blueprint(product_bp)

# Initialize Flask-Admin
# admin.init_app(app)

# @app.route('/admin')
# @admin_required
# def admin_index():
#     return redirect(url_for('admin.index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
