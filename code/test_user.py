from unittest import TestCase
from Game_logic import Image, User

class TestUser(TestCase):
    def test_tagImage(self):
        user = User(0)
        image = Image(0)
        user.tagImage(image, 'first')
        self.assertEqual(user.getScore(), 1)
        user.tagImage(image, 'first')
        self.assertEqual(user.getScore(), 2)
        self.assertEqual(image.tags, ['first'])


    def test_getScore(self):
        user = User(0)
        self.assertEqual(user.getScore(), 0)
