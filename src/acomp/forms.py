from wtforms import Form, StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import InputRequired, EqualTo, Length, Regexp
from wtforms.widgets import HTMLString, html_params
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from acomp import app
from acomp.auth import auth


class HTML5TextWidget(object):
    """
    From https://github.com/wtforms/wtforms/issues/337:
    Renders a text input w/ html5 minlength maxlength required data-error pattern.
    Based on WTF Validators.
    """
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        # ToDo: find out how 'type' can be inherited
        app.logger.debug(field.type)
        if (str(field.type) == 'StringField'):
            kwargs.setdefault('type', 'text')
        else:
            kwargs.setdefault('type', 'password')

        for validator in field.validators:
            if isinstance(validator, Length):
                # add min legnth
                min_length = getattr(validator, 'min')
                if min_length not in (-1, None):
                    kwargs.setdefault('minlength', min_length)
                    kwargs.setdefault('required', "")
                # add max length
                max_length = getattr(validator, 'max')
                if max_length not in (-1, None):
                    kwargs.setdefault('maxlength', max_length)
            if isinstance(validator, Regexp):
                # add pattern
                pattern = getattr(validator, 'regex')
                if pattern is not None:
                    kwargs.setdefault('pattern', pattern.pattern)

        return HTMLString('<input {params}>'.format(params=self.html_params(name=field.name, **kwargs)))


def UniqueName(form, field):
    """
    Username must be unique
    """
    if auth.exists(field.data):
        raise ValidationError('This username is already taken, please choose another one')


class Signup(FlaskForm):
    csrf = CSRFProtect(app)

    loginname = StringField("Name", validators=[
        InputRequired(message='Username must be provided'),
        Length(min=1, max=512, message='Please use not more than 512 characters'),
        Regexp('^\\w+$', message='Please use alphanumeric characters'),
        UniqueName,
    ], widget=HTML5TextWidget())
    loginpswd = PasswordField("Password", validators=[
        InputRequired(message='Password must be provided'),
        Length(min=14, max=512, message='Please make sure to confirm your password'),
    ], widget=HTML5TextWidget())
    loginpswdConfirm = PasswordField("Confirm", validators=[
        InputRequired(message='Password must be confirmed'),
        Length(min=14, max=512, message='Please make sure to confirm your password'),
        EqualTo('loginpswd', message='Please make sure to confirm your password'),
    ], widget=HTML5TextWidget())
    submit = SubmitField("Register")


class Signin(FlaskForm):
    csrf = CSRFProtect(app)

    loginname = StringField("Name", validators=[
        InputRequired(message='Username must be provided'),
        Length(min=1, max=512, message='Username too long'),
        Regexp('^\\w+$', message='Invalid username'),
    ])
    loginpswd = PasswordField("Password", validators=[
        InputRequired(message='Password must be provided'),
        Length(min=1, max=512, message='Password too long'),
    ])
    submit = SubmitField("Login")
