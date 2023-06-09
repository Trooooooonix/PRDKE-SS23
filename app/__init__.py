from flask import Flask
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

# The __init__.py-file serves the application as entry point and initializer for packages
#       and constraints such as CORS. CORS gives the put in Ports permission to request and send Data.

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": [
                            "http://127.0.0.1:50050",
                            "http://127.0.0.1:50052",
                            "http://localhost:50050",
                            "http://localhost:50052"]}})

bootstrap = Bootstrap(app)

# database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# login
login = LoginManager(app)
# makes the login necessary
login.login_view = 'login'

from app import routes, models