from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

# database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# login
login = LoginManager(app)
# makes the login necessary
login.login_view = 'login'


from app import routes, models