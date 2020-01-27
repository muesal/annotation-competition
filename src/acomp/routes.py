from flask import flash, make_response, render_template, redirect, request, session, url_for
from acomp import app, db, loginmanager, sessions
from flask_login import current_user, login_required, logout_user
from urllib.parse import urlparse, urljoin
from acomp.glUser import GLUser
from acomp.auth import auth

from acomp.forms import Captcha, Classic, Signup, Signin, SettingsUserName, SettingsChangePassword, \
    SettingsDeleteAccount
import json

loginmanager.login_view = 'login'


def is_safe_url(target):
    """ https://web.archive.org/web/20120517003641/http://flask.pocoo.org/snippets/62/ """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


@app.route('/classic')
@login_required
def classic():
    form = Classic()
    usr = GLUser(current_user.get_id())
    user_name = usr.getName()
    img = usr.startClassic()
    return render_template('classic.html', source=img['images'], form=form, username=user_name)


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
            res_data = {'accepted': tag[0], 'message': tag[1], 'score': tag[2]}
            res = make_response(res_data)
            res.headers.set('Content-Type', 'application/json')
            return res


@app.route('/captcha')
@login_required
def captcha():
    form = Captcha()
    usr = GLUser(current_user.get_id())
    user_name = usr.getName()
    images = usr.startCaptcha()
    return render_template('captcha.html', source=images['images'], form=form, username=user_name)


@app.route('/captcha/data', methods=['GET'])
@login_required
def captcha_get():
    usr = GLUser(current_user.get_id())
    try:
        data = usr.startCaptcha()
        app.logger.debug(data)
        res = make_response(json.dumps(data))
    except Exception as e:
        return bad_request(e)
    else:
        res.headers.set('Content-Type', 'application/json')
        return res


@app.route('/captcha/data', methods=['POST'])
@login_required
def captcha_post():
    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'joker' in data:
        usr = GLUser(current_user.get_id())
        try:
            wrng_images = usr.jokerCaptcha()
        except Exception as e:
            return bad_request(e)
        else:
            res_data = {"message": wrng_images}
            res = make_response(json.dumps(res_data))
            res.headers.set('Content-Type', 'application/json')
            return res
    if 'captcha' in data:
        usr = GLUser(current_user.get_id())
        try:
            captcha = usr.capCaptcha(data['captcha'])
        except Exception as e:
            return bad_request(e)
        else:
            res_data = {'accepted': captcha[0], 'message': captcha[1], 'score': captcha[2]}
            res = make_response(res_data)
            res.headers.set('Content-Type', 'application/json')
            return res
    else:
        return bad_request('Missing key in JSON.')


@app.route('/quiz')
def quiz():
    if current_user.is_authenticated:
        return redirect(url_for('tutorial'))
    if 'quiz' not in session:
        session['quiz'] = 0
    if session['quiz'] >= app.config['ACOMP_QUIZ_POINTS']:
        flash('Congrats, you have reached enough points!')
    form = Captcha()
    usr = GLUser(-1)
    images = usr.startCaptcha()
    app.logger.debug('Current quiz score: {}'.format(session['quiz']))
    return render_template('captcha.html', source=images['images'], form=form)


@app.route('/quiz/data', methods=['GET'])
def quiz_get():
    if 'quiz' not in session:
        return forbidden('Not authorized.')
    if session['quiz'] >= app.config['ACOMP_QUIZ_POINTS']:
        flash('Congrats, you have reached enough points!')

    usr = GLUser(-1)
    try:
        data = usr.startCaptcha()
        app.logger.debug(data)
        res = make_response(json.dumps(data))
    except Exception as e:
        return bad_request(e)
    else:
        res.headers.set('Content-Type', 'application/json')
        return res


@app.route('/quiz/data', methods=['POST'])
def quiz_post():
    if 'quiz' not in session:
        return forbidden('Not authorized.')

    data = request.get_json()
    if data is None:
        return bad_request('Invalid JSON.')
    if 'captcha' not in data:
        return bad_request('Missing key in JSON.')
    else:
        usr = GLUser(-1)
        try:
            challange, captcha = usr.capEntryQuiz(data['captcha'])
        except Exception as e:
            return bad_request(e)
        else:
            session['quiz'] += 1 if challange == 1 else -1
            signup_permission = int(session['quiz'] >= app.config['ACOMP_QUIZ_POINTS'])

            data = {'OK': signup_permission, 'message': captcha[0]}
            res = make_response(data)
            res.headers.set('Content-Type', 'application/json')
            return res


@app.route('/tutorial')
def tutorial():
    form = Classic()
    return render_template('tutorial.html', source='../static/img/tutorial_1.jpg', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('settings'))
    form = Signup()
    if 'quiz' not in session:
        flash('Please solve the quiz first')
        return redirect('quiz')
    elif session['quiz'] < app.config['ACOMP_QUIZ_POINTS']:
        flash('Please solve the quiz first')
        return redirect('quiz')
    elif form.validate_on_submit():
        auth.register(form.loginname.data, form.loginpswd.data, form.loginpswdConfirm.data)
        auth.login(form.loginname.data, form.loginpswd.data)
        flash('Thanks for registering')
        return redirect(url_for('tutorial'))
    app.logger.debug('Current quiz score: {}'.format(session['quiz']))
    return render_template('signup.html', form=form)


@app.route('/signup/data', methods=['POST'])
@app.route('/settings/data', methods=['POST'])
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('settings'))
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
            else:
                return redirect(url_for('classic'))
        except Exception as e:
            flash(e)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    nameform = SettingsUserName()
    passwordform = SettingsChangePassword()
    deleteform = SettingsDeleteAccount()
    usr = GLUser(current_user.get_id())
    user_name = usr.getName()

    if nameform.validate_on_submit():
        try:
            app.logger.debug('Change name to {}'.format(nameform.newloginname.data))
            usrname = auth.changename(current_user.get_id(), nameform.newloginname.data, nameform.loginpswd.data)
            flash('Name change successful')
            app.logger.debug('Current user id {}'.format(current_user.get_id()))
            app.logger.debug('Name change for {}'.format(usrname))
        except Exception as e:
            flash(e)

    if passwordform.validate_on_submit():
        try:
            usr_id = auth.changetoken(current_user.get_id(), passwordform.oldpswd.data, passwordform.newpswd.data,
                                      passwordform.newpswdConfirm.data)
            if usr_id > 0:
                flash('Password change successful')
                app.logger.debug('Current user id {}'.format(current_user.get_id()))
                app.logger.debug('Change password for {}'.format(usr_id))
        except Exception as e:
            flash(e)

    if deleteform.validate_on_submit():
        try:
            app.logger.debug('Delete user id {}'.format(current_user.get_id()))
            usrname = auth.delete(current_user.get_id(), deleteform.loginpswddelform.data)
            app.logger.debug('Deleted user {}'.format(usrname))
            flash('User deleted')
            return redirect(url_for('login'))
        except Exception as e:
            flash(e)

    return render_template('settings.html', nameform=nameform, deleteform=deleteform, passwordform=passwordform,
                           username=user_name)


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/highscore')
@login_required
def highscore():
    usr = GLUser(current_user.get_id())
    user_name = usr.getName()
    return render_template('highscore.html', highscore=usr.getHighscore(), username=user_name)


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
