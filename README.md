# Annotation Competition

Annotation Competition or _AComp_ is a gamificated process to add tags to an 
existing set of images.
You can find addidional information in `docs/gamemodes.md`.

## Setup

First you have to create a file `src/acomp/config.py` that conatins 
a `SECRET_KEY` and a `SQLALCHEMY_DATABASE_URI` 
(e.g. `SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/acomp.sqlite3'`)

### Quick start using Docker

Run the following commands in the root directory of this repository:

1. `docker build -t acomp src/`
2. `docker run -it -v $PWD/src:/app -p127.0.0.1:5000:5000 acomp`

You can now access the service in your favorite browser at 
`http://localhost:5000`.

### Running tests

Test are located in `acomp/tests`. You can run them with the following commands:

1. `pip install nose`
2. `nosetests -v`

This works in a Docker environment too!