from flask import render_template
from acomp import app


@app.route('/')
@app.route('/home')
@app.route('/classic')
def classic():
    return render_template('index.html', source='/static/img/test.png', width=800, height=600)


@app.errorhandler(400)
def bad_request(e):
    return render_template('4xx.html', error_msg=e), 400


@app.errorhandler(401)
def forbidden(e):
    return render_template('4xx.html', error_msg=e), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('4xx.html', error_msg=e), 404
