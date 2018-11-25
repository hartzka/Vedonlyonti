from flask import Flask
app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy
import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vedonlyonti.db"    
    app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

# login functionality
from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.setup_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = "Please login to use this functionality."

from application import views

from application.auth import models
from application.auth import views

from application.tilitapahtuma import models
from application.tilitapahtuma import views

from application.veto import models
from application.veto import views

from application.laji import models

from application.tapahtuma import models
from application.tapahtuma import views
from application.tapahtuma import forms

from application.tapahtumaveto import models

from application.joukkue import models

from application.tapahtumajoukkue import models


# login functionality, part 2
from application.auth.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# database creation
try: 
    db.create_all()
except:
    pass

