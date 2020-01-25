import nltk
import os
from acomp import app


@app.cli.command("nltk-data")
def data():
    nltk.download('popular', download_dir=os.environ['NLTK_DATA'])
