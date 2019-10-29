from unittest import TestCase
from Game_logic import Image


class TestImage(TestCase):
    def test_levelUp0(self):
        image = Image(0)
        image.levelUp()
        self.assertTrue(image.level == 0)

    def test_levelUp1(self):
        image = Image(0)
        image.tags = ['a', 'b', 'c']
        image.levelUp()
        self.assertTrue(image.level == 1)

    def test_levelUp2(self):
        image = Image(0)
        image.tags = ['a', 'b', 'c', 'd', 'e']
        image.levelUp()
        self.assertTrue(image.level == 2)

    def test_addTag_first(self):
        image = Image(0)
        self.assertTrue(image.addTag('a') == 1)
        self.assertEqual(image.tags, ['a'])

    def test_addTag_second(self):
        image = Image(0)
        self.assertTrue(image.addTag('a') == 1)
        self.assertTrue(image.addTag('b') == 1)
        self.assertEqual(image.tags, ['a', 'b'])

    def test_addTag_sameTag(self):
        image = Image(0)
        self.assertTrue(image.addTag('a') == 1)
        self.assertTrue(image.addTag('b') == 1)
        self.assertTrue(image.addTag('b') == 1)
        self.assertEqual(image.tags, ['a', 'b'])

    def test_addTag_level1(self):
        image = Image(0)
        image.tags = ['a', 'b']
        self.assertTrue(image.addTag('c') == 1)
        self.assertTrue(image.level == 1)
        self.assertTrue(image.addTag('c') == 2)
        self.assertTrue(image.addTag('d') == 1)
        self.assertEqual(image.tags, ['a', 'b', 'c', 'd'])

    def test_addTag_level2(self):
        image = Image(0)
        image.tags = ['a', 'b', 'c', 'd']
        self.assertTrue(image.addTag('e') == 2)
        self.assertTrue(image.level == 2)
        self.assertTrue(image.addTag('a') == 0)
        self.assertTrue(image.addTag('c') == 2)
        self.assertEqual(image.tags, ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(image.forbiddenTags, ['a', 'b'])
