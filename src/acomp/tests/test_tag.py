from unittest import TestCase
from acomp.gamelogic import GLTag


class TestTag(TestCase):
    def test_mentioned(self):
        image_id = 1
        tag = GLTag('a', image_id)
        tag.mentioned()
        self.assertEqual(tag.getFrequency(), 2)

    def test_word(self):
        image_id = 1
        tag = GLTag('a', image_id)
        self.assertEqual(tag.getWord(), 'a')
