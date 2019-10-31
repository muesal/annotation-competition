from flask import send_from_directory
from acomp import app
from acomp.models import Image, Tag, User


@app.route('/')
def index():
    return send_from_directory("html/", 'index.html')
