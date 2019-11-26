from flask import make_response, render_template, request, session, url_for
from acomp import app, db, sessions
from acomp.glUser import GLUser
from acomp.glImage import GLImage
from acomp.models import User, Image


@app.route('/')
@app.route('/home')
@app.route('/classic')
def classic():
    token = request.args.get('token')
    if 'userid' in session:
        app.logger.debug("UserID: %s", session['userid'])
        if token is None:
            # TODO: create new user
            # Test usr
            new_usr = User('guest', 'myverysecret')
            db.session.add(new_usr)
            db.session.commit()
            app.logger.debug("New user")
        else:
            # TODO: verify existing user
            app.logger.debug("Existing user")
    else:
        # TODO: individual userid
        session['userid'] = 'guest'
    # TODO: individual userid
    usr = GLUser(1)
    img = usr.startClassic()
    return render_template('index.html', source=img['images'], width=800, height=600)


@app.route('/classic/data', methods=['GET'])
def classic_data_get():
    if 'userid' in session:
        # TODO: individual userid
        usr = GLUser(1)
        try:
            res = app.make_response(usr.startClassic())
        except Exception as e:
            return bad_request(e)
        else:
            res.headers.set('Content-Type', 'application/json')
            return res
    else:
        return forbidden('Not authorized.')


@app.route('/classic/data', methods=['POST'])
def classic_data_post():
    if 'userid' in session:
        data = request.get_json()
        if data is None:
            return bad_request('Invalid JSON.')
        if 'Tag' not in data:
            return bad_request('Missing key in JSON.')
        else:
            # TODO: individual userid
            usr = GLUser(1)
            try:
                res = usr.tagImage(data['Tag'])
            except Exception as e:
                return bad_request(e)
            else:
                res.headers.set('Content-Type', 'application/json')
                return '{"OK":"200", "message":"' + res[1] + '"}'
    else:
        return forbidden('Not authorized.')


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
