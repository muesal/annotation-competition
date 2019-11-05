from unittest import TestCase
from acomp.gamelogic import GLImage, GLUser, GLTag


class TestUser(TestCase):
    def test_tagImage(self):
        user = GLUser('franz')
        image = GLImage(1)
        user.tagImage(image, 'first')
        self.assertEqual(user.getScore(), 1)
        user.tagImage(image, 'second')
        self.assertEqual(user.getScore(), 2)
        self.assertEqual(image.tags[0].getWord(), 'first')
        self.assertEqual(len(image.tags), 2)

    def test_getScore(self):
        user = GLUser('franz')
        self.assertEqual(user.getScore(), 0)