from unittest import TestCase
from acomp.Game_logic import Image, User, Tag


class TestUser(TestCase):
    def test_tagImage(self):
        user = User(0)
        image = Image(0)
        user.tagImage(image, 'first')
        self.assertEqual(user.getScore(), 1)
        user.tagImage(image, 'first')
        self.assertEqual(user.getScore(), 2)
        self.assertEqual(image.tags[0].getWord(), 'first')
        self.assertEqual(len(image.tags), 1)

    def test_getScore(self):
        user = User(0)
        self.assertEqual(user.getScore(), 0)
