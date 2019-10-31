from acomp import app
from acomp.models import Image, Tag, User


@app.route('/')
def hello_world():
    return 'Hello, Annotation Competition!'
