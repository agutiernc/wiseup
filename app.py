from flask import Flask, redirect, render_template, session, request, g, flash
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, Favorites
from forms import UserForm, LoginForm, UpdateEmailForm, UpdatePasswordForm
from reddit_api import res_top, res_joke, get_comments
import random

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///wiseup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'thesecretishere'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

bcrypt = Bcrypt()


###########################################################################
# get api data

def get_data(data):
    '''Retrieve JSON data.'''

    post_info = []

    for post in data.json()['data']['children']:
        title = filter_title(post['data']['title']) if data == res_top else post['data']['title']
        self_text = post['data']['selftext'] if data == res_joke else None
        comments = get_comments(post['data']['permalink']) if data == res_top else None

        post_info.append({ 
            'title': title,
            'url': post['data']['url'],
            'id': post['data']['id'],
            'selftext': self_text,
            'comments': comments
        })
    
    return post_info


def filter_title(title):
    '''Remove common words/characters at the start of a title.'''

    words = ['today i learned', 'that', 'about', '-', 'of', ':']
    new_title = title.split(' ', 1)[1].split() # remove 'TIL' from string

    # if title contains any word in words, remove it
    if new_title[0] in words:
        new_title.pop(0)

    return ' '.join(new_title).capitalize()


@app.route('/')
def main_page():
    '''Main page w/links to login or user registration.'''

    if not g.user:
        return render_template('/index.html')
    
    return redirect(f'/users/{ g.user.username }')


##############################################################################
# User signup/login/logout routes

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    '''Login user.'''

    session[CURR_USER_KEY] = user.id


def do_logout():
    '''Logout user.'''

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/register/', methods=['GET', 'POST'])
def register_user():
    ''' Display and process new user registration form.
    
        If form not valid, present form. Otherwise, redirect to main page.

        If there already is a user with that username: flash message
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

            # confirm registration
            flash('Thank you for registering. Please login')
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another.')

            return render_template('/users/register.html', form=form)

        do_login(new_user)

        return redirect('/login')
    else:
        return render_template('/users/register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    ''' Handle user login and add to session.
        
        If username/password is valid, redirect to user's feed.
    '''

    form = LoginForm()

    if form.validate_on_submit():
        # authenticate user
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)

            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    
    return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout_user():
    '''Logout user and remove from session.'''

    do_logout()

    return redirect('/')


##############################################################################
# User's home page, favorites, and account settings routes


@app.route('/users/<username>/')
def show_home(username):
    '''Display user's feed.'''

    # only logged in user can view
    if not g.user:
        return redirect('/login')
    
    # get user info
    user = User.query.filter_by(username=g.user.username).first()

    # get all of user's saved posts
    favs = user.favorites

    top_posts = get_data(res_top)

    jokes = get_data(res_joke)

    random_posts = random.sample(top_posts, 5)

    random_joke = random.sample(jokes, 1)

    return render_template('/users/home.html', jokes=random_joke, user=user, favs=favs, top=random_posts)


@app.route('/users/<username>/settings/', methods=['GET', 'POST'])
def users_profile(username):
    '''Display user's settings and allow to update/delete account.'''

    if not g.user:
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

            # confirm update
            flash('E-mail has been updated')

            return redirect(f'/users/{username}/settings/')
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

            # confirm update
            flash('Password has been updated')

            return redirect(f'/users/{username}/settings/')
        else:
            email_form.password.errors = ['Invalid password']
    
    return render_template('/users/profile.html', user=user, form1=email_form, form2=pswd_form)


@app.route('/users/<username>/save/', methods=['POST'])
def add_favs(username):
    '''Let current user save/unsave a post.'''

    # only logged in user can view
    if not g.user:
        return redirect('/login')

    # get user info
    user = User.query.filter_by(username=g.user.username).first()
    
    # get json data from axios
    title = request.json['title']
    url = request.json['url']
    reddit_id = request.json['id']
    comments = request.json['comments']

    # check if reddit id exists in user's saved posts
    find_val = Favorites.query.filter((Favorites.reddit_id == reddit_id) & (Favorites.user_id == user.id))

    if db.session.query(find_val.exists()).scalar():
        # remove saved posts if it already exists in Favorites
        db.session.delete(find_val.first())
        db.session.commit()

    else:
        saved_post = Favorites(
            user_id = user.id,
            reddit_id = reddit_id,
            type = 'til',
            title = title,
            url = url,
            comments = comments
        )
        
        # save and commit to db
        db.session.add(saved_post)
        db.session.commit()

    return redirect('/users/{username}')
    

@app.route('/users/delete', methods=["POST"])
def delete_user():
    '''Delete user.'''

    # only current user can delete their own account
    if not g.user:
        return redirect('/login')
    
    # delete user from db
    db.session.delete(g.user)
    db.session.commit()

    # deletion confirmation
    flash('Sorry to see you go. If you change your mind, please re-register.')

    return redirect('/')


def update_pswd(password):
    '''Update user password.'''
    
    hashed = bcrypt.generate_password_hash(password)

    # turn byte string into normal (unicode utf8) string
    hashed_utf8 = hashed.decode('utf8')
    
    return hashed_utf8