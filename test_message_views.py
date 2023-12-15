"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        self.u1 = User.signup("u1", "u1@email.com", "password", None)
        self.u2 = User.signup("u2", "u2@email.com", "password", None)
        db.session.flush()

        self.m1 = Message(text="m1-text", user_id=self.u1.id)
        db.session.add_all([self.m1])
        db.session.commit()

# class MessageAddViewTestCase(MessageBaseViewTestCase):
#     def test_add_message_form(self):
#         """Should load add message form"""

#         with app.test_client() as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.u1.id

#             resp = c.get("/messages/new")
#             html = resp.get_data(as_text=True)

#             self.assertEqual(resp.status_code, 200)
#             self.assertIn("Comment for messages/create.html loaded.", html)

    # def test_add_message(self):
    #     """Should be able to add messages"""

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u1.id

    #         resp = c.post("/messages/new", data={"text": "Hello"})

    #         self.assertEqual(resp.status_code, 302)

    #         self.assertIsNotNone(Message
    #                              .query
    #                              .filter_by(text="Hello")
    #                              .one_or_none())
    #         self.assertEqual(Message.query.count(), 2)
    #         self.assertNotIn(self.m1.id, self.u2.messages)

    # def test_add_message_unauth(self):
    #     """Should not be able to add messages if not logged-in"""

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = None

    #         resp = c.post("/messages/new", follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 401)
    #         self.assertIn("Unauthorized", html)

    # def test_delete_message(self):
    #     """Should be able to delete messages"""

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u1.id

    #         resp = c.post(f"/messages/{self.m1.id}/delete")

    #         self.assertEqual(resp.status_code, 302)

    #         self.assertIsNone(Message
    #                              .query
    #                              .filter_by(text=self.m1.text)
    #                              .one_or_none())
    #         self.assertEqual(Message.query.count(), 0)

    # def test_delete_message_unauth(self):
    #     """
    #     Should not be able to delete message if not original poster/authorized
    #     """

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u2.id

    #         resp = c.post(
    #             f"/messages/{self.m1.id}/delete",
    #             follow_redirects=True
    #         )

    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 401)
    #         self.assertIn("Unauthorized", html)

    # def test_show_messages_with_delete_button_shown(self):
    #     """Should show message. Show delete button for own user's message"""

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u1.id

    #         resp = c.get(
    #             f"/messages/{self.m1.id}",
    #             follow_redirects=True
    #         )

    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(self.m1.text, html)
    #         self.assertIn('Delete', html)
    #         self.assertIn("Comment for messages/show.html loaded.", html)

    # def test_show_messages_without_delete_button_shown(self):
    #     """Should show message. Do not show delete button if not owned"""

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u2.id

    #         resp = c.get(
    #             f"/messages/{self.m1.id}",
    #             follow_redirects=True
    #         )

    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(self.m1.text, html)
    #         self.assertNotIn('Delete', html)
    #         self.assertIn("Comment for messages/show.html loaded.", html)


    # def test_show_messages_unauth(self):
    #     """Should not show message if unauthorized"""

    #     with app.test_client() as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = None

    #         resp = c.get(
    #             f"/messages/{self.m1.id}",
    #             follow_redirects=True
    #         )

    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized", html)
    #         self.assertNotIn("Comment for messages/show.html loaded.", html)

    def test_like_message(self):
        """Should be able to like a message"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id

            resp = c.post(f'/messages/{self.m1.id}/like')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/messages/{self.m1.id}')

            self.assertIn(self.m1, self.u2.messages_liked)

            self.assertIsNotNone(Like
                                 .query
                                 .filter_by(message_id=self.m1.id)
                                 .one_or_none())
            self.assertEqual(Like.query.count(), 1)

            resp = c.get(resp.location)
            html = resp.get_data(as_text=True)

            self.assertIn("bi-star-fill", html)

    def test_like_message_self(self):
        """Should not be able to like own message"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.post(f'/messages/{self.m1.id}/like')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/messages/{self.m1.id}')

            self.assertNotIn(self.m1, self.u1.messages_liked)

            self.assertIsNone(Like
                                 .query
                                 .filter_by(message_id=self.m1.id)
                                 .one_or_none())
            self.assertEqual(Like.query.count(), 0)

            resp = c.get(resp.location)
            html = resp.get_data(as_text=True)

            self.assertIn("You cannot like your own Warble!", html)
            self.assertNotIn("bi-star-fill", html)


#test show liekd Messages
#test add message
# test show message
#test delete message
#test like message
#test unlike message

# def test_new_note_ok(self):
#         with app.test_client() as client:
#             with client.session_transaction() as sess:
#                 sess["username"] = "user-1"
#             resp = client.post(
#                 "/users/user-1/notes/new",
#                 data={
#                     "title": "Title",
#                     "content": "Content",
#                 }
#             )
#             self.assertEqual(resp.status_code, 302)
#             self.assertEqual(resp.location, "/users/user-1")

#             self.assertEqual(Note.query.count(), 2)