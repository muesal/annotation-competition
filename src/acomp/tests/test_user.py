from unittest import TestCase
from acomp import db
from acomp.models import User, Image
from acomp.glImage import GLImage
from acomp.glUser import GLUser


class TestUser(TestCase):

    def setUp(self):
        try:
            self.user = GLUser(1)
        except Exception as e:
            print("Empty User table, creating new user")
            user = User('hans', 'top-secret')
            db.session.add(user)
            db.session.commit()
            self.user = GLUser(1)

        self.user.startClassic()
        self.image_id = 2
        self.image = GLImage(self.image_id)

    def test_startClassic(self):
        image_fn = self.user.startClassic()
        self.assertIsNotNone(image_fn)
        Image.query.filter_by(filename=image_fn)

    def test_tagImage(self):
        val, mes = self.user.tagImage('first', self.image)
        self.assertEqual(val, 0)
        self.assertEqual(mes, 'first')
        self.assertEqual(self.user.getScore(), 1)
        self.assertIsNotNone(self.image.getTag('first'))

    def test_tagImage_wrongGameMode(self):
        self.user.startCaptcha()
        val, mes = self.user.tagImage('first', self.image)
        self.assertEqual(val, -1)
        self.assertEqual(mes, 'Wrong game mode')

        self.user.end()
        val, mes = self.user.tagImage('first', self.image)
        self.assertEqual(val, -1)
        self.assertEqual(mes, 'Wrong game mode')
        self.user.startClassic()

    def test_tagImage_sameTagTwice(self):
        self.user.tagImage('first', self.image)
        val, mes = self.user.tagImage('first', self.image)
        self.assertEqual(val, -1)
        self.assertEqual(mes, 'You already provided this tag for this image')

    def test_tagImage_threeWords(self):
        val, mes = self.user.tagImage('first and second', self.image)
        self.assertEqual(val, -1)
        self.assertEqual(mes, 'A tag may not be longer than two words.')

    def test_tagImage_misspelled(self):
        val, mes = self.user.tagImage('blubeldio', self.image)
        self.assertEqual(val, -1)
        self.assertEqual(mes, 'This word(s) could not be found in our dictionary.')

    def test_skip(self):
        image_fn = self.user.startClassic()
        image = Image.query.filter_by(filename=image_fn).one_or_none()
        skips = image.skips
        score = self.user.skip()
        self.assertEqual(image.skips, skips + 1)

    def test_end(self):
        self.assertIsNotNone(self.user.end())
