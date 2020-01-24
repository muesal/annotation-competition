from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
from googletrans import Translator
from nltk.stem import WordNetLemmatizer

app = Flask(__name__, template_folder='templates')
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
sessions = Session(app)
loginmanager = LoginManager(app)
wl = WordNetLemmatizer()
tl = Translator()

from acomp import routes
from acomp import prefill
from acomp import data
