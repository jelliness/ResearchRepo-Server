from .auth import auth
from .fetch_data import data
from .users import users

def register_routes(app):
    # Register the blueprint for routes
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(data, url_prefix='/data')
    app.register_blueprint(users, url_prefix='/users')