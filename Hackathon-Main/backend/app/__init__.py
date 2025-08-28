from flask import Flask


def create_app():
    # Create the Flask application instance
    app = Flask(__name__)

    # Basic configuration: a secret key for session security
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!

    # Import and register our database functions with the app
    from app import database
    # This tells Flask to run close_db() when cleaning up after a request
    app.teardown_appcontext(database.close_db)

    # Import and register our API routes
    from app import routes
    app.register_blueprint(routes.bp)

    return app