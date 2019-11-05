from unittest import TestCase
from acomp.gamelogic import GLImage, GLTag


class TestImage(TestCase):
    def test_levelUp0(self):
        image = GLImage(1)
        image.levelUp()
        self.assertEqual(image.level, 0)

    def test_levelUp1(self):
        image = GLImage(1)
        image.addTag('a')
        image.addTag('b')
        image.addTag('c')
        image.printTags()
        self.assertEqual(image.level, 1)

    def test_levelUp2(self):
        image = GLImage(1)
        image.addTag('a')
        image.addTag('b')
        image.addTag('c')
        image.addTag('d')
        image.addTag('e')
        self.assertEqual(image.level, 2)

    def test_addTag_first(self):
        image = GLImage(1)
        self.assertEqual(image.addTag('a'), 1)

    def test_addTag_second(self):
        image = GLImage(1)
        self.assertEqual(image.addTag('a'), 1)
        self.assertEqual(image.addTag('b'), 1)

    def test_addTag_sameTag(self):
        image = GLImage(1)
        self.assertEqual(image.addTag('a'), 1)
        self.assertEqual(image.addTag('b'), 1)
        self.assertEqual(image.addTag('b'), 1)
        self.assertEqual(image.getTag('b').getFrequency(), 2)

    def test_addTag_level1(self):
        image = GLImage(1)
        image.addTag('a')
        image.addTag('b')
        self.assertEqual(image.addTag('c'), 1)
        self.assertEqual(image.level, 1)
        self.assertEqual(image.addTag('c'), 2)
        self.assertEqual(image.addTag('d'), 1)

    def test_addTag_level2(self):
        image = GLImage(1)
        image.addTag('a')
        image.addTag('b')
        image.addTag('c')
        image.addTag('d')
        self.assertEqual(image.addTag('e'), 2)
        self.assertEqual(image.level, 2)
        self.assertEqual(image.addTag('a'), 0)
        self.assertEqual(image.addTag('c'), 2)

    def test_validate_wrong(self):
        image = GLImage(1)
        self.assertEqual(image.validate('blublio'), -1)

    def test_validate_misspelled(self):
        image = GLImage(1)
        self.assertNotEqual(image.validate('ertz'), -1)

    def test_validate_uppercase(self):
        image = GLImage(1)
        image.addTag('SHERLOCK')
        self.assertNotEqual(image.getTag('sherlock'), None)

    def test_validate_twoWords(self):
        image = GLImage(1)
        self.assertEqual(image.addTag('Sherlock Holmes'), 1)
        self.assertNotEqual(image.getTag('Sherlock Holmes'), None)
        self.assertEqual(image.addTag('Sherlock Holmes and Watson'), 0)


    def test_getTag(self):
        image = GLImage(1)
        image.addTag('a')
        image.addTag('b')
        image.addTag('b')
        image.addTag('c')
        image.addTag('d')
        tag = image.getTag('b')
        self.assertEqual(tag.getFrequency(), 2)
        self.assertEqual(tag.getWord(), 'b')
        tag = image.getTag('c')
        #self.assertEqual(tag.getFrequency(1), 1)
        self.assertEqual(tag.getWord(), 'c')

    def test_getTag_invalid(self):
        image = GLImage(1)
        self.assertEqual(image.getTag('a'), None)