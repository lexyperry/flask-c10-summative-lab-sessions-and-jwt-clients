from flask import Flask
from flask_migrate import Migrate

# Import database and bcrypt from models
from models import db, bcrypt
# Import the API resource routing from resources.py
from resources import api

# Initialize the Flask application
app = Flask(__name__)
# Set configuration values
# Connect to a local SQLite database and prevent tracking modifications
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.from_object('config.Config') # Load additional config from config.py
app.secret_key = "super-secret"# Used to sign session cookies

# Initialize extensions with the app context
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# Register all API routes from resources.py
api.init_app(app)

# Run the Flask development server
if __name__ =="__main__":
    app.run(debug=True)