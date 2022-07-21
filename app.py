from flask import Flask, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from psycopg2 import IntegrityError
from models import connect_db, db, User
from forms import UserForm, LoginForm
from reddit_api import get_data, res_new, res_top

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wiseup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'thesecretishere'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def main_page():
    '''Main page w/links to login or user registration.'''

    return redirect('/register')

##############################################################################
# User signup/login/logout

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    '''Display and process user registration form.'''

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data

        new_user = User.register(username, password, email)

        # add user to db
        db.session.add(new_user)

        try:
            # commit new user to db
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another.')

            return render_template('/users/register.html', form=form)
        
        # add user to session when registered
        session['username'] = new_user.username

        return render_template('secret.html')
    else:
        return render_template('/users/register.html', form=form)

@app.route('/logout')
def logout_user():
    '''Logout user and remove from session.'''

    session.pop('username')

    return redirect('/')