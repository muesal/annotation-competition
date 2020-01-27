from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
from googletrans import Translator
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from spellchecker.spellchecker import SpellChecker

app = Flask(__name__, template_folder='templates')
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
sessions = Session(app)
loginmanager = LoginManager(app)
wn.ensure_loaded()
wl = WordNetLemmatizer()
tl = Translator()
sc = SpellChecker(distance=1)

from acomp import routes
from acomp import prefill
from acomp import data
