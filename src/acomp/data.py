import nltk
from acomp import app


@app.cli.command("nltk-data")
def data():
    nltk.download('popular')
