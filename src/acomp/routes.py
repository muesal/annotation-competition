from flask import render_template, request, session, url_for
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
    img_id = usr.startClassic()
    img = Image.query.get(img_id)
    return render_template('index.html', source=url_for('static', filename='images/' + img.filename), width=800, height=600)


@app.route('/classic/data', methods=['GET'])
def classic_data_get():
    if 'userid' in session:
        # TODO: individual userid
        usr = GLUser(1)
        img_id = usr.startClassic()
        img = Image.query.get(img_id)
        img_obj = GLImage(img_id)
        data: dict = {}
        data['images'] = url_for('static', filename='images/' + img.filename)
        data['timelimit'] = app.config['ACOMP_CLASSIC_TIMELIMIT']
        data['accepted'] = img_obj.printTags()
        data['score'] = usr.getScore()
        # TODO: individual userid
        data['user'] = '1'

        res = app.make_response(data)
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
        if 'Content' not in data:
            return bad_request('Missing key in JSON.')
        else:
            # TODO: individual userid
            usr = GLUser(1)
            usr.tagImage(data['Content'])
            return '{"OK":"200"}'
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
