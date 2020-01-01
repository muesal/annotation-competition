from flask import flash, make_response, render_template, redirect, request, url_for
from acomp import app, db, loginmanager
from flask_login import current_user, login_required, logout_user
from urllib.parse import urlparse, urljoin
from acomp.glUser import GLUser
from acomp.auth import auth
from acomp.forms import Captcha, Classic, Signup, Signin
import json

loginmanager.login_view = 'login'


def is_safe_url(target):
    """ https://web.archive.org/web/20120517003641/http://flask.pocoo.org/snippets/62/ """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@app.route('/home')
@app.route('/classic')
@login_required
def classic():
    form = Classic()
    usr = GLUser(current_user.get_id())
    img = usr.startClassic()
    return render_template('index.html', source=img['images'], form=form)


@app.route('/classic/data', methods=['GET'])
@login_required
def classic_data_get():
    usr = GLUser(current_user.get_id())
    try:
        data = usr.startClassic()
        app.logger.debug(data)
        res = make_response(json.dumps(data))
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
        usr = GLUser(current_user.get_id())
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
            app.logger.debug('Login user name {}'.format(form.loginname.data))
            usr_id = auth.login(form.loginname.data, form.loginpswd.data)
            if usr_id > 0:
                flash('Login successful')
                app.logger.debug('Login user id {}'.format(usr_id))
                app.logger.debug('Current user id {}'.format(current_user.get_id()))
                target = request.args.get('next')
            if not is_safe_url(target):
                return bad_request('Could not redirect to ' + target)
        except Exception as e:
            flash(e)
    return render_template('login.html', form=form)


@app.route('/captcha')
@login_required
def captcha():
    form = Captcha()
    usr = GLUser(current_user.get_id())
    images = usr.startCaptcha()
    return render_template('captcha.html', source=images['images'], form=form)


@app.route('/captcha/data', methods=['GET'])
@login_required
def captcha_get():
#    usr = GLUser(current_user.get_id())
#    try:
#        data = usr.startCaptcha()
#        app.logger.debug(data)
#        res = make_response(json.dumps(data))
#    except Exception as e:
#        return bad_request(e)
#    else:
#        res.headers.set('Content-Type', 'application/json')
#        return res
    test_images = ["static/img/test.png", "static/img/test_alt.png"]
    data = {'image': test_images, 'tags': ['house', 'sun', 'flower']}
    res = make_response(data)
    res.headers.set('Content-Type', 'application/json')
    return res


@app.route('/captcha/data', methods=['POST'])
@login_required
def captcha_post():
    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'captcha' not in data:
        return bad_request('Missing key in JSON.')
    else:
        usr = GLUser(current_user.get_id())
        try:
            tag = usr.tagImage(data['tag'])
        except Exception as e:
            return bad_request(e)
        else:
            data = '{"OK":"200", "message":"' + tag[1] + '"}'
            res = make_response(data)
            res.headers.set('Content-Type', 'application/json')
            return res


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/highscore')
def highscore():
    usr = GLUser(current_user.get_id())
    return render_template('highscore.html', highscore=usr.getHighscore())


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


@app.route('/tutorial')
def tutorial():
    form = Classic()
    return render_template('tutorial.html', source='../static/img/tutorial_1.jpg', form=form)


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
