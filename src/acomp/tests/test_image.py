from unittest import TestCase
from acomp.gamelogic import GLImage, GLUser


class TestImage(TestCase):
    def setUp(self):
        self.image = GLImage(1)
        self.user1 = GLUser('fritz1')
        self.user2 = GLUser('fritz2')
        self.user3 = GLUser('fritz3')
        self.user4 = GLUser('fritz4')
        self.user5 = GLUser('fritz5')

    def test_levelUp0(self):
        self.user1.tagImage(self.image, 'a')  # has score 0
        self.assertEqual(self.image.level, 0)  # level
        self.assertEqual(self.user1.getScore(), 1)  # score of user1

    def test_levelUp1(self):
        self.user1.tagImage(self.image, 'a')
        self.user2.tagImage(self.image, 'a')  # has score 1
        self.user3.tagImage(self.image, 'a')
        self.assertEqual(self.image.level, 1)

        self.assertEqual(self.user2.getScore(), 1)
        self.user2.tagImage(self.image, 'a')  # adds already known tag
        self.assertEqual(self.user2.getScore(), 1 + 2)  # -> score + 2
        self.user2.tagImage(self.image, 'b')  # adds new tag
        self.assertEqual(self.user2.getScore(), 1 + 2 + 1)  # -> score + 1

    def test_levelUp2(self):
        self.user1.tagImage(self.image, 'a')
        self.user2.tagImage(self.image, 'a')
        self.user3.tagImage(self.image, 'a')
        self.user4.tagImage(self.image, 'a')  # has score 2 (added known tag to level1 image -> score + 2)
        self.user5.tagImage(self.image, 'a')
        self.assertEqual(self.image.level, 2)

        self.assertEqual(self.user4.getScore(), 2)
        self.user4.tagImage(self.image, 'a')  # adds already known tag
        self.assertEqual(self.user4.getScore(), 2 + 2)  # -> score + 2
        self.user4.tagImage(self.image, 'c')  # adds new tag
        self.assertEqual(self.user4.getScore(), 2 + 2 + 2)  # -> score + 2

    def test_addTag_sameTag(self):
        self.assertEqual(self.image.addTag('z'), 1)
        self.assertEqual(self.image.addTag('z'), 1)
        self.assertEqual(self.image.getTag('z').getFrequency(), 2)

    def test_validate_wrong(self):
        self.assertEqual(self.image.validate('blublio'), -1)

    def test_validate_misspelled(self):
        self.assertNotEqual(self.image.validate('ertz'), -1)

    def test_validate_uppercase(self):
        self.image.addTag('SHERLOCK')
        self.assertNotEqual(self.image.getTag('sherlock'), None)

    def test_validate_twoWords(self):
        self.assertNotEqual(self.image.addTag('Sherlock Holmes'), 0)
        self.assertNotEqual(self.image.getTag('Sherlock Holmes'), None)
        self.assertEqual(self.image.addTag('Sherlock Holmes and Dr. Watson'), 0)

    def test_getTag(self):
        self.image.addTag('y')
        self.image.addTag('y')
        tag = self.image.getTag('y')
        self.assertEqual(tag.getFrequency(), 2)
        self.assertEqual(tag.getWord(), 'y')

    def test_getTag_invalid(self):
        self.assertEqual(self.image.getTag('x'), None)
