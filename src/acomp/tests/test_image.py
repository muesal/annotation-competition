from unittest import TestCase
from acomp.glImage import GLImage
from acomp.glUser import GLUser
from acomp.models import Image, Tag, User, ImageTag, user_image
from acomp import db


class TestImage(TestCase):
    def setUp(self):
        self.image_id = 1
        self.image = GLImage(self.image_id)
        self.user1 = User('fritz1', 'top-secret')
        self.user2 = User('fritz2', 'top-secret')
        self.user3 = User('fritz3', 'top-secret')
        self.user4 = User('fritz4', 'top-secret')
        self.user5 = User('fritz5', 'top-secret')
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.add(self.user3)
        db.session.add(self.user4)
        db.session.add(self.user5)
        db.session.commit()

        self.user1 = GLUser(self.user1.id)
        self.user2 = GLUser(self.user2.id)
        self.user3 = GLUser(self.user3.id)
        self.user4 = GLUser(self.user4.id)
        self.user5 = GLUser(self.user5.id)

        self.user1.game_mode = 0
        self.user2.game_mode = 0
        self.user3.game_mode = 0
        self.user4.game_mode = 0
        self.user5.game_mode = 0

    def test_levelUp0(self):
        try:
            self.user1.user.seen.append(Image.query.get(self.image_id))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        score = self.user1.getScore()
        self.user1.tagImage('a', self.image)
        self.assertEqual(self.user1.getScore(), score + 1)  # score of user1

        self.image.levelUp()
        self.assertEqual(self.image.level, 0)  # level

    def test_levelUp1(self):
        try:
            self.user2.user.seen.append(Image.query.get(self.image_id))
            self.user3.user.seen.append(Image.query.get(self.image_id))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        self.user2.tagImage('a', self.image)
        self.user3.tagImage('b', self.image)

        self.image.levelUp()
        self.assertEqual(self.image.level, 1)

        self.user1.image_level = 1
        self.user2.image_level = 1
        self.user3.image_level = 1
        self.user4.image_level = 1
        self.user5.image_level = 1

        score = self.user2.getScore()
        self.assertIsNotNone(self.image.hasTag('b'))
        self.user2.tagImage('b', self.image)  # adds already known tag
        self.assertEqual(self.user2.getScore(), score + 2)  # -> score + 2
        self.user2.tagImage('c', self.image)  # adds new tag
        self.assertEqual(self.user2.getScore(), score + 2 + 1)  # -> score + 1

    def test_levelUp2(self):
        try:
            self.user4.user.seen.append(Image.query.get(self.image_id))
            self.user5.user.seen.append(Image.query.get(self.image_id))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        self.user4.tagImage('a', self.image)  # has score 2 (added known tag to level1 image -> score + 2)
        self.user5.tagImage('d', self.image)

        self.image.levelUp()
        self.assertEqual(self.image.level, 2)

        self.user1.image_level = 2
        self.user2.image_level = 2
        self.user3.image_level = 2
        self.user4.image_level = 2
        self.user5.image_level = 2

        score = self.user4.getScore()
        self.user4.tagImage('d', self.image)  # adds already known tag
        self.assertEqual(self.user4.getScore(), score + 2)  # -> score + 2
        self.user4.tagImage('e', self.image)  # adds new tag
        self.assertEqual(self.user4.getScore(), score + 2 + 2)  # -> score + 2

    def test_validate_wrong(self):
        self.assertRaises(Exception, self.image.validate, 'blublio')

    def test_validate_misspelled(self):
        self.assertNotEqual(self.image.validate('ertz'), -1)

    def test_validate_uppercase(self):
        self.image.tag('SHERLOCK')
        self.assertIsNotNone(self.image.hasTag('sherlock'))

    def test_validate_twoWords(self):
        self.assertNotEqual(self.image.tag('Sherlock Holmes')[0], 0)
        self.assertIsNotNone(self.image.hasTag('Sherlock Holmes'))
        self.assertRaises(Exception, self.image.validate, 'Sh er lock')

    def test_getTag(self):
        self.image.tag('y')
        self.image.tag('y')
        tag = self.image.hasTag('y')
        self.assertEqual(tag.getFrequency(), 2)
        self.assertEqual(tag.getWord(), 'y')

    def test_getTag_invalid(self):
        self.assertIsNone(self.image.hasTag('x'))

    # TODO: Test forbidden tags
