from acomp import db


user_image = db.Table('user_image', db.Model.metadata,
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class ImageTag(db.Model):
    __tablename__ = 'image_tag'
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    frequency = db.Column('frequency', db.Integer, db.CheckConstraint('frequency >= 0'), default=1, nullable=False)
    successful_verified = db.Column('successful_verified', db.Integer, db.CheckConstraint('successful_verified >= 0'), default=0, nullable=False)
    total_verified = db.Column('total_verified', db.Integer, db.CheckConstraint('total_verified >= 0'), default=0, nullable=False)
    tag = db.relationship('Tag', back_populates='images')
    image = db.relationship('Image', back_populates='tags')



class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, unique=True, nullable=False)
    skips = db.Column(db.Integer, db.CheckConstraint('skips >= 0'), nullable=False, default=0)
    tags = db.relationship('ImageTag', back_populates='image')

    def __init__(self, filename):
        self.filename = filename


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    images = db.relationship('ImageTag', back_populates='tag')

    def __init__(self, name):
        self.name = name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    secret = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, db.CheckConstraint('score >= 0'), nullable=False)
    seen = db.relationship('Image', secondary='user_image', backref='seen')

    def __init__(self, username, secret, score=0):
        self.username = username
        self.secret = secret
        self.score = score
