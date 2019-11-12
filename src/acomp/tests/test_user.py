from unittest import TestCase
from acomp.gamelogic import GLImage, GLUser, GLTag


class TestUser(TestCase):

    def setUp(self):
        self.user = GLUser('franz')
        self.image_id = 3
        self.image = GLImage(self.image_id)

    def test_tagImage(self):
        self.user.tagImage(self.image, 'first')
        self.assertEqual(self.user.getScore(), 1)
        self.user.tagImage(self.image, 'second')
        self.assertEqual(self.user.getScore(), 2)
        self.assertEqual(self.image.tags[0].getWord(), 'first')
        self.assertEqual(len(self.image.tags), 2)
