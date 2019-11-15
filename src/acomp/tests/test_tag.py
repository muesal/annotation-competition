from unittest import TestCase
from acomp.glTag import GLTag


class TestTag(TestCase):

    def setUp(self):
        self.image_id = 2
        self.tag = GLTag('a', self.image_id)

    def test_mentioned(self):
        self.tag.mentioned()
        self.assertEqual(self.tag.getFrequency(), 2)

    def test_word(self):
        self.assertEqual(self.tag.getWord(), 'a')
