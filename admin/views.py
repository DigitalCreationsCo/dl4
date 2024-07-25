from flask import redirect, url_for, session, abort, request
from functools import wraps
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from models import User, Product, DownloadLink, db

# Custom AdminIndexView to enforce admin access
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if 'user_id' not in session:
            return False
        user = User.query.get(session['user_id'])
        return user and user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

class UserModelView(ModelView):
    def is_accessible(self):
        if 'user_id' not in session:
            return False
        user = User.query.get(session['user_id'])
        return user and user.is_admin

class ProductModelView(ModelView):
    def is_accessible(self):
        if 'user_id' not in session:
            return False
        user = User.query.get(session['user_id'])
        return user and user.is_admin

class DownloadLinkModelView(ModelView):
    def is_accessible(self):
        if 'user_id' not in session:
            return False
        user = User.query.get(session['user_id'])
        return user and user.is_admin

# Setup Flask-Admin
admin = Admin(
    name='Digital Product Admin',
    template_mode='bootstrap3',
    index_view=MyAdminIndexView()
)
admin.add_view(UserModelView(User, db.session))
admin.add_view(ProductModelView(Product, db.session))
admin.add_view(DownloadLinkModelView(DownloadLink, db.session))
# admin.add_view(FileAdmin('downloads/', '/downloads/', name='Files'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
