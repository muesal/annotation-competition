from flask import render_template, request, session, url_for
from acomp import app, glUser, sessions


@app.route('/')
@app.route('/home')
@app.route('/classic')
def classic():
    if 'user' in session:
        print(session['user'])
    else:
        session['user'] = 'guest'
    return render_template('index.html', source=url_for('static', filename='img/test.png'), width=800, height=600)


@app.route('/classic/data', methods=['GET'])
def classic_data_get():
    if 'user' in session:
        data: dict = {}
        data['images'] = url_for('static', filename='img/test.png')
        data['timelimit'] = app.config['ACOMP_CLASSIC_TIMELIMIT']
        data['accepted'] = ''
        data['score'] = '0'
        data['user'] = '0'

        res = app.make_response(data)
        res.headers.set('Content-Type', 'application/json')
        return res
    else:
        return forbidden('Not authorized.')


@app.route('/classic/data', methods=['POST'])
def classic_data_post():
    if 'user' in session:
        data = request.get_json()
        if data is None:
            return bad_request('Invalid JSON.')
        else:
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
