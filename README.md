# Annotation Competition

Annotation Competition, or _AComp_, is a gamificated process to add tags to an 
existing set of images.
You can find addidional information in `docs/gamemodes.md`.

This appliation is powered by [Flask](https://flask.palletsprojects.com) and 
[Python 3](https://www.python.org/).

## Setup

First you have to create a file `src/acomp/config.py` that conatins 
a `SECRET_KEY`, a `SQLALCHEMY_DATABASE_URI` 
(e.g. `SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/acomp.sqlite3'`) and 
a `SESSION_TYPE` (e.g. `SESSION_TYPE = 'filesystem'`).

You may want to set `NLTK_DATA` to use a custom location for the natural 
language toolkit files.

### Getting started

Run the following commands in the `src` directory:

1. `pip install -r requirements.txt`
2. `flask nltk-data`
3. `flask db uprade`
4. `flask run`

If you have any existing images to import you can run 
`flask prefill /my/image/folder`.

If you'd like to provide tags in another language than english, you may change 
`ACOMP_LANGUAGE_DEFAULT`  in `config.py` to the 
[ISO-639-1-code](http://www.loc.gov/standards/iso639-2/php/code_list.php) of 
your preferred language. However, all messages are not yet provided in other 
languages than english, and the response to your provided tags may be confusing.
We recommend playing in english.

### Quick start using Docker

Run the following commands in the root directory of this repository:

1. `docker build -t acomp src/`
2. `docker run --rm -v $PWD/src:/app -p127.0.0.1:5000:5000 acomp`

You can now access the service in your favorite browser at 
`http://localhost:5000`.

**Note:** With this example any changed data will be lost when you stop the 
conatiner! We'll provide a production ready example in the future.

### Running tests

Test are located in `acomp/tests`. You can run them with the following commands:

1. `pip install nose`
2. `nosetests -v`

This works in a Docker environment too!
