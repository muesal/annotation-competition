from flask import flash, make_response, render_template, redirect, request, session, url_for
from acomp import app, db, sessions, loginmanager
from flask_login import current_user, login_user, login_required, logout_user
from acomp.glUser import GLUser
from acomp.auth import auth
from acomp.forms import Signup, Signin
import json


loginmanager.login_view = 'login'


@app.route('/home')
@app.route('/classic')
@login_required
def classic():
    usr = GLUser(current_user)
    img = usr.startClassic()
    return render_template('index.html', source=img['images'])


@app.route('/classic/data', methods=['GET'])
@login_required
def classic_data_get():
    usr = GLUser(current_user)
    try:
        dict = usr.startClassic()
        app.logger.debug(dict)
        res = make_response(json.dumps(dict))
    except Exception as e:
        return bad_request(e)
    else:
        res.headers.set('Content-Type', 'application/json')
        return res


@app.route('/classic/data', methods=['POST'])
@login_required
def classic_data_post():
    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'tag' not in data:
        return bad_request('Missing key in JSON.')
    else:
        usr = GLUser(current_user)
        try:
            tag = usr.tagImage(data['tag'])
        except Exception as e:
            return bad_request(e)
        else:
            data = '{"OK":"200", "message":"' + tag[1] + '"}'
            res = make_response(data)
            res.headers.set('Content-Type', 'application/json')
            return res


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Signin()
    if form.validate_on_submit():
        try:
            user = auth.login(form.loginname.data, form.loginpswd.data)
            flash('Login successful')
            login_user(user)
        except Exception as e:
            flash(e)
    return render_template('login.html', form=form)


@app.route('/captcha')
def captcha():
    return render_template('captcha.html')


@app.route('/captcha/data', methods=['GET'])
def captcha_get():
    test_images = ["static/img/test.png", "static/img/test_alt.png"]
    stuff = {'image': test_images, 'tags': ['house', 'sun', 'flower']}
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Signup()
    if form.validate_on_submit():
        auth.register(form.loginname.data, form.loginpswd.data, form.loginpswdConfirm.data)
        flash('Thanks for registering')
    return render_template('signup.html', form=form)


@app.route('/signup/data', methods=['POST'])
def signup_post():
    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'name' not in data:
        return bad_request('Missing key in JSON.')
    else:
        if (auth.exists(data['name'])):
            return '{"available":"0", "message":"Username not available"}'
        else:
            return '{"available":"1", "message":"Username available"}'


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
