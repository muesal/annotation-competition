from flask import session
from flask_bcrypt import Bcrypt
from acomp import app, db, loginmanager, sessions
from acomp.models import User


@loginmanager.user_loader
def load_user(usr_id):
    return User.query.get(usr_id)

class auth:
    """ :return whether a username exists in the database or not """
    def checkAvailability(username: str) -> bool:
        return db.session.query(db.exists().where(User.username == username)).scalar()

    """ :return  the id of the logged in user """
    def login(username: str, token: str) -> int:
        bcrypt = Bcrypt(app)

        usr = User.query.filter_by(username=username).one_or_none()
        if usr is None:
            raise Exception('A user with this username could not be found. The username was: {}'.format(username))

        if bcrypt.check_password_hash(usr.token, token):
            print("It Matches!")
        else:
            print("It Does not Match :(")

        return usr.id

    """ :return  the id of the registered user """
    def register(username: str, token: str, tokenVerify: str) -> int:
        bcrypt = Bcrypt(app)

        if auth.checkAvailability(username):
            raise Exception('A user with this username is already registered. The username was: {}'.format(username))

        if token != tokenVerify:
            raise Exception('The given passwords do not match.')

        tokenHash = bcrypt.generate_password_hash(token)

        try:
            new_usr = User(username, tokenHash)
            db.session.add(new_usr)
            db.session.commit()
            app.logger.debug("New user: {}".format(username))
            usr = User.query.filter_by(username=username).one_or_none()
        except Exception as e:
            app.logger.debug(e)
            db.session.rollback()

        return usr.id
