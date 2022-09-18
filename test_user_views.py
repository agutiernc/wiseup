"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, User, Favorites

os.environ['DATABASE_URL'] = "postgresql:///wiseup-test"

from app import app, CURR_USER_KEY

# create database
db.create_all()

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Disable CSRF
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    '''Test views for users.'''

    def setUp(self):
        '''Create test client, add sample data.'''

        # clean up database of old data
        db.drop_all()
        db.create_all()

        User.query.delete()
        Favorites.query.delete()

        # register users
        user1 = User.register(
            username='tester1',
            email='tester1@tests.com',
            password='Password1!'
        )

        user1.id = 2

        user2 = User.register(
            username='tester2',
            email='tester2@tests.com',
            password='Password2!'
        )

        user2.id = 3

        # add and commit users to database
        db.session.add_all([user1, user2])
        db.session.commit()

        # get users' info
        u1 = User.query.get(user1.id)
        u2 = User.query.get(user2.id)

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()


    def tearDown(self):
        '''Clean up fouled transactions.'''

        db.session.rollback()


    def test_save_unsave_fav(self):
        '''Test for when user saves/unsaves a post.'''

        title = 'TIL in 400 BCE Persian engineers created a ice machine in the desert.'
        url = 'https://www.reddit.com/r/todayilearned/comments/xb0in6/til_in_400_bce_persian_engineers_created_a_ice/'
        comments = 'So, basically, thousands of years ago, Persians noticed that ice would build up overnight in the shadows.'

        data = {
            "user_id": self.u1.id,
            "id": "xb0in6",
            "type": "til",
            "url": url,
            "title": title,
            "comments": comments
        }

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            # test when user saves a post
            res = c.post(f'/users/{self.u1.username}/save', json=data, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            user = User.query.get(2)

            self.assertEqual(len(user.favorites), 1)
            self.assertEqual(user.favorites[0].reddit_id, 'xb0in6')

            # test when user unsaves post from above
            res2 = c.post(f'/users/{self.u1.username}/save', json=data, follow_redirects=True)

            self.assertEqual(res2.status_code, 200)
            
            favs = Favorites.query.filter_by(reddit_id='xb0in6').all()

            self.assertEqual(len(favs), 0)

    
    def test_delete_user(self):
        '''Test for when user deletes their account.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            res = c.post('/users/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            users = User.query.all()

            # only one user should exist
            self.assertEqual(len(users), 1)


    def test_registration(self):
        '''Test user registration.'''

        data = {
            'username': 'tester',
            'password': 'Password$1',
            'confirm': 'Password$1',
            'email': 'tester3@testing.com'
        }

        with self.client as c:
            res = c.post('/register/', data=data, follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            users = User.query.all()

            self.assertEqual(len(users), 3)

            new_user = User.query.get(1)

            self.assertEqual(new_user.email, 'tester3@testing.com')

    
    def test_login(self):
        '''Test login.'''

        data = {
            'username': 'tester1',
            'password': 'Password1!'
        }

        with self.client as c:
            res = c.post('/login/', data=data, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Welcome <strong>tester1</strong>', res.data)

    
    def test_logout(self):
        '''Test logout.'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = c.get('/logout', follow_redirects=True)

            self.assertEqual(res.status_code, 200)

            self.assertIn(b'<h1 class="mb-3">Today YOU Learn...</h1>', res.data)

