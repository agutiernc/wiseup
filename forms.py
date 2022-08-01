from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp

class UserForm(FlaskForm):
    '''User registration form.'''

    username = StringField('Username',
                validators=[
                    InputRequired(),
                    Length(min=5, max=20,
                        message='Username must be 5 to 20 characters long')
                ])
    
    password = PasswordField('Password',
                validators=[
                    InputRequired(),
                    Length(min=6, message='Password must be 6 or more characters long'),
                    EqualTo('confirm', message='Passwords must match'),
                    Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{6,}$',
                            message='Password requirements invalid')
                ])

    confirm = PasswordField('Repeat Password', validators=[InputRequired()])

    email = EmailField('Email',
                validators=[
                    InputRequired(),
                    Email(),
                    Length(min=3, max=50)
                ])


class LoginForm(FlaskForm):
    '''Login Form.'''

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])


class UpdateEmailForm(FlaskForm):
    '''Update Email for profile.'''

    password = PasswordField('Current Password', validators=[InputRequired(), Length(min=6)])

    email = EmailField('Email',
                validators=[
                    InputRequired(),
                    Email(),
                    Length(min=3, max=50)
                ])

    submit1 = SubmitField('Update Email')


class UpdatePasswordForm(FlaskForm):
    '''Update email form for profile.'''

    password = PasswordField('Current Password',
                validators=[InputRequired(), Length(min=6)])
    
    new_pswd = PasswordField('New Password',
                validators=[InputRequired(),
                    Length(min=6, message='Password must be 6 or more characters long'),
                    EqualTo('confirm', message='Passwords must match'),
                    Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{6,}$',
                            message='Password requirements invalid')
                ])
    
    confirm = PasswordField('Confirm Password', validators=[InputRequired()])

    submit2 = SubmitField('Update Password')