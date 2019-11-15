from unittest import TestCase
from acomp.glImage import GLImage
from acomp.glUser import GLUser


class TestUser(TestCase):

    def setUp(self):
        self.user = GLUser('franz')
        self.image_id = 3
        self.image = GLImage(self.image_id)

    def test_startClassic(self):
        image_id = self.user.startClassic()
        self.assertIsNotNone(image_id)
        GLImage(image_id)

    def test_tagImage(self):
        self.user.tagImage('first', self.image)
        self.assertEqual(self.user.getScore(), 1)
        self.user.tagImage('second', self.image)
        self.assertEqual(self.user.getScore(), 2)
        self.assertEqual(self.image.tags[0].getWord(), 'first')
        self.assertEqual(len(self.image.tags), 2)

    def test_end(self):
        self.assertIsNotNone(self.user.end())
