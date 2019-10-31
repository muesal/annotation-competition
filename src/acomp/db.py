# These env variables are the same ones used for the DB container
#user = os.environ['POSTGRES_USER']
#pwd = os.environ['POSTGRES_PASSWORD']
#db = os.environ['POSTGRES_DB']
host = 'db' # docker-compose creates a hostname alias with the service name
port = '5432' # default postgres port 
#engine = create_engine('postgres://%s:%s@%s:%s/%s' % (user, pwd, host, port, db))
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

Base = declarative_base()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)
