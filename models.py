from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    '''Connect to database.'''

    db.app = app
    db.init_app(app)

class User(db.Model):
    '''User schema for database.'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(20), nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String(50), nullable=False, unique=True)

    favorites = db.relationship('Favorites', cascade='all, delete')

    @classmethod
    def register(cls, username, password, email):
        '''Register user with hashed password and return user.'''

        hashed = bcrypt.generate_password_hash(password)

        # turn byte string into normal (unicode utf8) string
        hashed_utf8 = hashed.decode('utf8')

        user = cls(
            username=username,
            password=hashed_utf8,
            email=email
        )
        
        return user

    @classmethod
    def authenticate(cls, username, password):
        '''Validate user and password.'''

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Favorites(db.Model):
    '''A user's favorite posts or jokes.'''

    __tablename__= 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable=False
    )

    reddit_id = db.Column(db.Text, nullable=False)

    type = db.Column(db.String(4), nullable=False)

    title = db.Column(db.Text, nullable=False)

    url = db.Column(db.Text)

    text = db.Column(db.Text)

    comments = db.Column(db.ARRAY(db.Text()))

    # user = db.relationship('User')


# You can easily find records:
# Example.my_array.contains([1, 2, 3]).all()
# You can use text items of array
# db.Column(db.ARRAY(db.Text())
