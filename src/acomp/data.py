import nltk
import os
from acomp import app


@app.cli.command("nltk-data")
def data():
    nltk.download('popular', download_dir=os.getenv('NLTK_DATA', app.config['NLTK_DATA']))
    nltk.download('wordnet', download_dir=os.getenv('NLTK_DATA', app.config['NLTK_DATA']))
