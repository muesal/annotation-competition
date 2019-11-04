from flask import render_template, url_for
from acomp import app


@app.route('/')
@app.route('/home')
@app.route('/classic')
def classic():
    return render_template('index.html', source=url_for('static', filename='img/test.png'), width=800, height=600)


@app.route('/classic/data', methods=['GET'])
def classic_data_get():
    data: dict = {}
    data['images'] = url_for('static', filename='img/test.png')
    data['timelimit'] = app.config['ACOMP_CLASSIC_TIMELIMIT']
    data['accepted'] = ''
    data['score'] = '0'
    data['user'] = '0'

    res = app.make_response(data)
    res.headers.set('Content-Type', 'application/json')
    # return Response(data, mimetype='application/json')
    return res


@app.route('/classic/data', methods=['POST'])
def classic_data_post(request):
    # TODO: check for user/token
    data = request.get_json()
    return '{"OK":"200"}'


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
