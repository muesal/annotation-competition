from flask import send_from_directory, render_template
from acomp import app
from acomp.models import Image, Tag, User


@app.route('/')
def index():
    return render_template('index.html', source = '/static/img/test.png', width = 800, height = 600)
