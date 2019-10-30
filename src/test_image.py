from unittest import TestCase
from Game_logic import Image, Tag


class TestImage(TestCase):
    def test_levelUp0(self):
        image = Image(0)
        image.levelUp()
        self.assertTrue(image.level == 0)

    def test_levelUp1(self):
        image = Image(0)
        image.addTag('a')
        image.addTag('b')
        image.addTag('c')
        image.printTags()
        self.assertTrue(image.level == 1)

    def test_levelUp2(self):
        image = Image(0)
        image.addTag('a')
        image.addTag('b')
        image.addTag('c')
        image.addTag('d')
        image.addTag('e')
        self.assertTrue(image.level == 2)

    def test_addTag_first(self):
        image = Image(0)
        self.assertTrue(image.addTag('a') == 1)

    def test_addTag_second(self):
        image = Image(0)
        self.assertTrue(image.addTag('a') == 1)
        self.assertTrue(image.addTag('b') == 1)

    def test_addTag_sameTag(self):
        image = Image(0)
        self.assertTrue(image.addTag('a') == 1)
        self.assertTrue(image.addTag('b') == 1)
        self.assertTrue(image.addTag('b') == 1)
        self.assertTrue(image.getTag('b').getFrequency() == 2)

    def test_addTag_level1(self):
        image = Image(0)
        image.addTag('a')
        image.addTag('b')
        self.assertTrue(image.addTag('c') == 1)
        self.assertTrue(image.level == 1)
        self.assertTrue(image.addTag('c') == 2)
        self.assertTrue(image.addTag('d') == 1)

    def test_addTag_level2(self):
        image = Image(0)
        image.addTag('a')
        image.addTag('b')
        image.addTag('c')
        image.addTag('d')
        self.assertTrue(image.addTag('e') == 2)
        self.assertTrue(image.level == 2)
        self.assertTrue(image.addTag('a') == 0)
        self.assertTrue(image.addTag('c') == 2)

    def test_validate_wrong(self):
        image = Image(0)
        self.assertTrue(image.validate('blublio') == -1)

    def test_validate_misspelled(self):
        image = Image(0)
        self.assertTrue(image.validate('ertz') != -1)

    def test_getTag(self):
        image = Image(0)
        image.addTag('a')
        image.addTag('b')
        image.addTag('b')
        image.addTag('c')
        image.addTag('d')
        tag = image.getTag('b')
        self.assertTrue(tag.getFrequency() == 2)
        self.assertTrue(tag.getWord() == 'b')
        tag = image.getTag('c')
        self.assertTrue(tag.getFrequency() == 1)
        self.assertTrue(tag.getWord() == 'c')

    def test_getTag_invalid(self):
        image = Image(0)
        self.assertTrue(image.getTag('a') == None)
