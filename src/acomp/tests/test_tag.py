from unittest import TestCase
from acomp.Game_logic import Tag


class TestTag(TestCase):
    def test_mentioned(self):
        tag = Tag('a', 0)
        tag.mentioned()
        self.assertEqual(tag.getFrequency(), 2)

    def test_word(self):
        tag = Tag('a', 0)
        self.assertEqual(tag.getWord(), 'a')
