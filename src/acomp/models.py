from acomp import db

image_tag = db.Table('image_tag', db.Model.metadata,
    db.Column('image_id', db.Integer, db.ForeignKey('Image.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('Tag.id'), primary_key=True),
    db.Column('frequency', db.Integer, db.CheckConstraint('frequency >= 0'), default=1, nullable=False),
    db.Column('successful_verified', db.Integer, db.CheckConstraint('successful_verified >= 0'), default=0, nullable=False),
    db.Column('total_verified', db.Integer, db.CheckConstraint('total_verified >= 0'), default=0, nullable=False)
)

user_image = db.Table('user_image', db.Model.metadata,
    db.Column('image_id', db.Integer, db.ForeignKey('Image.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
)


class Image(db.Model):
    __tablename__ = 'Image'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, unique=True, nullable=False)
    skips = db.Column(db.Integer, db.CheckConstraint('skips >= 0'), nullable=False, default=0)
    tags = db.relationship('Tag', secondary='image_tag', backref='tags')

    def __init__(self, filename):
        self.filename = filename


class Tag(db.Model):
    __tablename__ = 'Tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    secret = db.Column(db.String, nullable=True)
    score = db.Column(db.Integer, db.CheckConstraint('score >= 0'), nullable=False)
    seen = db.relationship('Image', secondary='user_image', backref='seen')

    def __init__(self, username, secret, score=0):
        self.username = username
        self.secret = secret
        self.score = score
