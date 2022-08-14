from flask import Flask, redirect, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, Favorites
from forms import UserForm, LoginForm, UpdateEmailForm, UpdatePasswordForm
from reddit_api import res_new, res_top, res_joke
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wiseup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'thesecretishere'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

bcrypt = Bcrypt()

def get_data(data):
    '''Retrieve JSON data.'''

    post_info = []

    for post in data.json()['data']['children']:
        # print(post['data']['title'])
        # print(post['data']['url'])

        post_info.append({ 
            'title': filter_title(post['data']['title']),
            'url': post['data']['url'],
            'id': post['data']['id']
        })
    
    return post_info


def filter_title(title):
    '''Remove common words at the start of a title.'''

    words = ['today i learned', 'that', 'about', '-', 'of']
    new_title = title.split(' ', 1)[1].split() # remove 'TIL' from string

    # if title contains any word in words, strip it
    if new_title[0] in words:
        new_title.pop(0)

    return ' '.join(new_title).capitalize()


@app.route('/')
def main_page():
    '''Main page w/links to login or user registration.'''

    return redirect('/register')


##############################################################################
# User signup/login/logout routes

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    ''' Display and process new user registration form.
    
        If form not valid, present form. Otherwise, redirect to main page.

        If the there already is a user with that username: flash message
        and redirect to form.
    '''

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' Handle user login and add to session.
        
        If username/password is valid, redirect to user's feed.
    '''

    form = LoginForm()

    if form.validate_on_submit():
        # authenticate user
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            # add user to session when logged in
            session['username'] = user.username

            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    
    return render_template('/users/login.html', form=form)



@app.route('/logout')
def logout_user():
    '''Logout user and remove from session.'''

    session.pop('username')

    return redirect('/')


##############################################################################
# User's home page, favorites, and account settings routes

@app.route('/users/<username>')
def show_home(username):
    '''Display user's feed.'''

    # only logged in user can view
    if 'username' not in session or username != session['username']:
        return redirect('/login')

    top_posts = get_data(res_top)

    random_posts = random.sample(top_posts, 5)

    return render_template('/users/home.html', top=random_posts)


@app.route('/users/<username>/save/<int:fav_id>', methods=['POST'])
def add_favs(username):
    '''Let current user save a post.'''

    # get user INFO
    # get all saved posts and then RENDER favs page

    # only logged in user can view
    if 'username' not in session or username != session['username']:
        return redirect('/login')

    # get user info
    user = User.query.filter_by(username=username).first()

    # fav_post = 

    # return render_template('/users/favs.html', user=user)
    return redirect('/users/{username}/saved')


@app.route('/users/<username>/saved')
def show_saved(username):
    '''Display user's saved posts.'''

    return render_template('favs.html')


@app.route('/users/<username>/settings', methods=['GET', 'POST'])
def users_profile(username):
    '''Display user's settings and allow to update/delete account.'''

    # only logged in user can view
    if 'username' not in session or username != session['username']:
        return redirect('/login')

    # get user info
    user = User.query.filter_by(username=username).first()

    # get forms' details
    email_form = UpdateEmailForm(obj=user)
    pswd_form = UpdatePasswordForm()

    # update email form
    if email_form.validate_on_submit():
        user.email = email_form.email.data
        password = email_form.password.data

        # authenticate user in order to update email
        if email_form.submit1.data and user.authenticate(username, password):
            # commit new data to db
            db.session.commit()

            return redirect(f'/users/{username}')
        else:
            email_form.password.errors = ['Invalid username/password']

    # update password form
    if pswd_form.submit2.data and pswd_form.validate_on_submit():
        password = pswd_form.password.data

        # authenticate user in order to update email
        if user.authenticate(username, password):
            user.password = update_pswd(pswd_form.new_pswd.data)

            # commit new data to db
            db.session.commit()

            return redirect(f'/users/{username}')
        else:
            email_form.password.errors = ['Invalid password']

    
    return render_template('/users/profile.html', user=user, form1=email_form, form2=pswd_form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    '''Delete user.'''

    # get user
    user = User.query.filter_by(username=session['username']).first()

    # only current user can delete their own account
    if 'username' not in session or user.username != session['username']:
        return redirect('/login')
    
    # delete user from db
    db.session.delete(user)
    db.session.commit()

    # remove user from session
    session.pop('username')

    return redirect('/')

def update_pswd(password):
    '''Update user password.'''
    hashed = bcrypt.generate_password_hash(password)

    # turn byte string into normal (unicode utf8) string
    hashed_utf8 = hashed.decode('utf8')
    
    return hashed_utf8


"""
    ToDos:
    add notifications
    style pages
    maybe add a form for user profile instead of UserForm
    organize data lists and add save icon
    get joke api working
        - joke is added to the top w/refresh button to get new joke
            - needs save icon too
"""