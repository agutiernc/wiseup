"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Favorites

os.environ['DATABASE_URL'] = "postgresql:///wiseup-test"

from app import app


class UserModelTestCase(TestCase):
    '''Test model for User.'''

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
    

    def test_user_model(self):
        u = User(
            email="test@test.com",
            username='testuser',
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # Test that new user has no favorites
        self.assertEqual(len(u.favorites), 0)

    
    def test_user_register(self):
        '''Testing register model.'''

        user_test = self.u1

        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, 'tester1')
        self.assertEqual(user_test.email, 'tester1@tests.com')
        self.assertNotEqual(user_test.password, 'Password1!')

        # test bcrypt hash password starts with $2b$12$
        self.assertTrue(user_test.password, '$2b$12$')

    
    def test_user_auth(self):
        '''Tests if user/password authenticates.'''

        user = User.authenticate(self.u1.username, 'Password1!')

        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u1.id)

        self.assertFalse(User.authenticate('fakename', 'pswd1'))
        self.assertFalse(User.authenticate(self.u1.username, 'badpswd'))


    def test_user_favorites(self):
        '''Test Favorites model.'''
        title = 'TIL in 400 BCE Persian engineers created a ice machine in the desert.'
        url = 'https://www.reddit.com/r/todayilearned/comments/xb0in6/til_in_400_bce_persian_engineers_created_a_ice/'
        comments = 'So, basically, thousands of years ago, Persians noticed that ice would build up overnight in the shadows.'

        fav = Favorites(
            user_id = self.u2.id,
            reddit_id = 'xb0in6',
            type = 'til',
            title = title,
            url = url,
            comments = comments
        )

        db.session.add(fav)
        db.session.commit()

        # Test that user has a favorite
        self.assertEqual(len(self.u2.favorites), 1)
        self.assertEqual(self.u2.favorites[0].reddit_id, 'xb0in6')
        self.assertEqual(self.u2.favorites[0].title, title)