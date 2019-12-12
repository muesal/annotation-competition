from flask import make_response, render_template, request, session, url_for
from acomp import app, db, sessions
from acomp.glUser import GLUser
from acomp.glImage import GLImage
from acomp.models import User, Image
import json


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
        # TODO: create new user
        # Test usr
        new_usr = User('guest', 'myverysecret')
        db.session.add(new_usr)
        db.session.commit()
        app.logger.debug("New user 2")
    # TODO: individual userid
    usr = GLUser(1)
    img = usr.startClassic()
    return render_template('index.html', source=img['images'])


@app.route('/classic/data', methods=['GET'])
def classic_data_get():
    if 'userid' in session:
        # TODO: individual userid
        usr = GLUser(1)
        try:
            dict = usr.startClassic()
            app.logger.debug(dict)
            res = make_response(json.dumps(dict))
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
        if 'tag' not in data:
            return bad_request('Missing key in JSON.')
        else:
            # TODO: individual userid
            usr = GLUser(1)
            try:
                tag = usr.tagImage(data['tag'])
            except Exception as e:
                return bad_request(e)
            else:
                data = '{"OK":"200", "message":"' + tag[1] + '"}'
                res = make_response(data)
                res.headers.set('Content-Type', 'application/json')
                return res
    else:
        return forbidden('Not authorized.')


@app.route('/captcha')
def captcha():
    return render_template('captcha.html')


@app.route('/captcha/data', methods=['GET'])
def captcha_get():
    test_images = ["static/img/test.png", "static/img/test_alt.png"]
    stuff = {'image': test_images}
    data = '{"OK":"200", "message":"' + json.dumps(stuff) + '"}'
    res = make_response(data)
    res.headers.set('Content-Type', 'application/json')


    res = make_response(stuff)
    res.headers.set('Content-Type', 'application/json')
    return res


@app.route('/captcha/data', methods=['POST'])
def captcha_post():
    if 'userid' in session:
        data = request.get_json()
        if data is None:
            return bad_request('Invalid JSON.')
        if 'captcha' not in data:
            return bad_request('Missing key in JSON.')
        else:
            # TODO: individual userid
            usr = GLUser(1)
            try:
                tag = usr.tagImage(data['tag'])
            except Exception as e:
                return bad_request(e)
            else:
                data = '{"OK":"200", "message":"' + tag[1] + '"}'
                res = make_response(data)
                res.headers.set('Content-Type', 'application/json')
                return res
    else:
        return forbidden('Not authorized.')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/data', methods=['POST'])
def login_post():
    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'name' not in data:
        return bad_request('Missing key in JSON.')
    else:
        return '{"OK":"200", "message":""}'


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup/data', methods=['POST'])
def signup_post():
    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'name' not in data:
        return bad_request('Missing key in JSON.')
    else:
        return '{"OK":"200", "message":""}'


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
