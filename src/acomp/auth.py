from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user
from acomp import app, db, loginmanager
from acomp.models import User


@loginmanager.user_loader
def load_user(usr_id):
    return User.query.get(usr_id)


class auth:
    """ :return whether a username exists in the database or not """
    def exists(username: str) -> bool:
        return db.session.query(db.exists().where(User.username == username)).scalar()

    """ :return the id of the logged in user """
    def login(username: str, token: str) -> int:
        usr_id = -1
        bcrypt = Bcrypt(app)

        usr = User.query.filter_by(username=username).one_or_none()
        if usr is None:
            raise Exception('A user with this username could not be found. The username was: {}'.format(username))

        if bcrypt.check_password_hash(usr.secret, token):
            app.logger.debug('Login: {}'.format(username))
            login_user(usr)
            usr_id = usr.id
        else:
            app.logger.debug('Failed login: '.format(username))
            raise Exception('Username/Password combination not found')

        return usr_id

    """ :return the id of the registered user """
    def register(username: str, token: str, tokenVerify: str) -> int:
        bcrypt = Bcrypt(app)

        if auth.exists(username):
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

    """ :return the name of the changed user """
    def changename(userid: int, newname: str, token: str) -> str:
        bcrypt = Bcrypt(app)

        usr = User.query.get(userid)
        if usr is None:
            raise Exception('A user with this id could not be found. The id was: {}'.format(userid))

        if bcrypt.check_password_hash(usr.secret, token):
            app.logger.debug('Verify: {}'.format(usr.username))
            try:
                usr.username = newname
                db.session.commit()
                app.logger.debug("Update username to: {}".format(newname))
            except Exception as e:
                app.logger.warn(e)
                db.session.rollback()
                raise Exception('Failed to update user')
        else:
            app.logger.debug('Failed to verify: '.format(usr.username))
            raise Exception('Username/Password combination not found')

        return usr.username

    """ :return the id of the updated user """
    def changetoken(userid: int, token: str, newToken: str, newTokenVerify: str) -> int:
        usr_id = -1
        bcrypt = Bcrypt(app)

        usr = User.query.get(userid)
        if usr is None:
            raise Exception('A user with this id could not be found. The id was: {}'.format(userid))

        if newToken != newTokenVerify:
            raise Exception('The given passwords do not match.')

        newTokenHash = bcrypt.generate_password_hash(newToken)

        if bcrypt.check_password_hash(usr.secret, token):
            app.logger.debug('Verify: {}'.format(usr.username))
            try:
                usr.secret = newTokenHash
                db.session.commit()
                app.logger.debug("Update secret for: {}".format(usr.username))
                usr_id = usr.id
            except Exception as e:
                app.logger.warn(e)
                db.session.rollback()
                raise Exception('Failed to update user')
        else:
            app.logger.debug('Failed to verify: '.format(usr.username))
            raise Exception('Username/Password combination not found')

        return usr_id

    """ :return the name of the deleted user """
    def delete(userid: int, token: str) -> str:
        bcrypt = Bcrypt(app)

        usr = User.query.get(userid)
        if usr is None:
            raise Exception('A user with this id could not be found. The id was: {}'.format(userid))

        if bcrypt.check_password_hash(usr.secret, token):
            app.logger.debug('Verify: {}'.format(usr.username))
            try:
                db.session.delete(usr)
                db.session.commit()
                logout_user()
                app.logger.debug("Drop user with username {}".format(usr.username))
            except Exception as e:
                app.logger.warn(e)
                db.session.rollback()
                raise Exception('Failed to drop user')
        else:
            app.logger.debug('Failed to verify: '.format(usr.username))
            raise Exception('Username/Password combination not found')

        return usr.username
