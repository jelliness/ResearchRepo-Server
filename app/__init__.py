from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mailman import Mail
from app.models import db, check_db
from app.config import Config  
from app.routes import register_routes
from sqlalchemy import inspect
from urllib.parse import urlparse
import redis

def initialize_db(app):
    """Initialize the database and check table creation."""
    db.init_app(app)
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    parsed_uri = urlparse(database_uri)

    db_user = parsed_uri.username
    db_password = parsed_uri.password
    db_host = parsed_uri.hostname
    db_port = parsed_uri.port
    db_name = parsed_uri.path.lstrip('/')

    check_db(
        db_name=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    
    with app.app_context():
        db.create_all()
        print("Tables created successfully.")
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        print("Database URL:", db.engine.url)
        print("Database Tables:", tables)
        
        if tables:
            print("Database setup complete with the following tables:", tables)
        else:
            print("Failed to create tables. Please check your models and database configuration.")

def initialize_routes(app):
    """Register application routes."""
    register_routes(app)

def initialize_redis(app):
    """Initialize Redis and attach it to the app."""
    redis_client = redis.StrictRedis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=True
    )
    app.redis_client = redis_client

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    JWTManager(app)
    Mail(app)

    # Initialize components
    initialize_db(app)
    initialize_routes(app)
    initialize_redis(app)

    return app
