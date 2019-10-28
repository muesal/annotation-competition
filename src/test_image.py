from unittest import TestCase
from Game_logic import Image


class TestImage(TestCase):
    def test_levelUp0(self):
        image = Image(0)
        image.levelUp()
        self.assertTrue(image.level == 0)

    def test_levelUp1(self):
        image = Image(0)
        image.tags = ['0', '1', '2']
        image.levelUp()
        self.assertTrue(image.level == 1)

    def test_levelUp2(self):
        image = Image(0)
        image.tags = ['0', '1', '2', '3', '4']
        image.levelUp()
        self.assertTrue(image.level == 2)

    def test_addTag_first(self):
        image = Image(0)
        self.assertTrue(image.addTag('first') == 1)
        self.assertEqual(image.tags, ['first'])

    def test_addTag_second(self):
        image = Image(0)
        self.assertTrue(image.addTag('first') == 1)
        self.assertTrue(image.addTag('second') == 1)
        self.assertEqual(image.tags, ['first', 'second'])

    def test_addTag_sameTag(self):
        image = Image(0)
        self.assertTrue(image.addTag('first') == 1)
        self.assertTrue(image.addTag('second') == 1)
        self.assertTrue(image.addTag('second') == 1)
        self.assertEqual(image.tags, ['first', 'second'])

    def test_addTag_level1(self):
        image = Image(0)
        image.tags = ['first', 'second']
        self.assertTrue(image.addTag('third') == 1)
        self.assertTrue(image.level == 1)
        self.assertTrue(image.addTag('third') == 2)
        self.assertTrue(image.addTag('fourth') == 1)
        self.assertEqual(image.tags, ['first', 'second', 'third', 'fourth'])

    def test_addTag_level2(self):
        image = Image(0)
        image.tags = ['first', 'second', 'third', 'fourth']
        self.assertTrue(image.addTag('fifth') == 2)
        self.assertTrue(image.level == 2)
        self.assertTrue(image.addTag('first') == 0)
        self.assertTrue(image.addTag('third') == 2)
        self.assertEqual(image.tags, ['first', 'second', 'third', 'fourth', 'fifth'])
        self.assertEqual(image.forbiddenTags, ['first', 'second'])
