from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app = Flask(__name__, template_folder='templates')
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
sessions = Session(app)

from acomp import routes
from acomp import prefill
