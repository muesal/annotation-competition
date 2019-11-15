from spellchecker.spellchecker import SpellChecker
from secrets import randbelow

from acomp import db
from acomp.models import Image, Tag, User, ImageTag, user_image
from acomp.glTag import GLTag

class GLImage:
    """
        A class used to represent an image

        Attributes:
            image (Image); the image
            id (int): id of the image
            tags ([Tag]): list of all the Tags provided for this image
            forbiddenTags [str]: string list of words which are forbidden to tag if image is in level 2
            level (int): level of this image (corresponds with the amount of provided Tags)
            spellcheck (SpellChecker): instance of the Spellchecker to check the spelling of new Tags
    """

    def __init__(self, id: int):
        # Todo: try....except for image query
        if id < 1:
            id = 1
        self.image = Image.query.get(id)
        self.id = id
        self.tags = []
        self.forbiddenTags = []
        self.level = 0
        self.spellcheck = SpellChecker(distance=1)

    def levelUp(self):
        """ Increase the level of the Image if necessary """
        query_image_user = User.query.join(user_image).join(Image).filter(
            user_image.c.image_id == self.id).all()
        tagged = len(query_image_user)
        if tagged > 2:
            self.level = 1
            if tagged > 4:
                self.level = 2
                # TODO: make this better (not alphabetically...)
                for i in range(2):
                    pass
                    #self.forbiddenTags.append(self.tags[i].name)

    def getLevel(self) -> int:
        """ :return the level of the image"""
        self.levelUp()
        return self.level

    def validate(self, word: str) -> int:
        """ Validates the Tag regarding his spelling (minor misspellings are corrected with frequency list algorithm of
            SpellChecker) and forbidden Tag list, if image in level 2.

            :param word: Tag to validate

            :return -1 if invalid, 0 if the tag was already known, 1 if he is valid and new for this picture
        """
        # word should not consist of more than two words
        word = word.split(" ")
        if len(word) > 2:
            return -1

        # for each word in tag: if unknown to dictionary: correct if minor error, else Tag is invalid
        wrong = list(self.spellcheck.unknown(word))
        if len(wrong) > 0:
            for i in range(len(wrong)):
                word[i] = self.spellcheck.correction(wrong[i])
                if word[i] == wrong[i]:
                    return -1

        # should be one string again
        word = (' '.join(word)).lower()

        # invalid if image is level 2 and Tag is forbidden
        if self.level == 2 and word in self.forbiddenTags:
            return -1

        # Tag is valid: add Tag or increase its frequency, return 0 if the tag was already known, 1 otherwise
        if len(self.tags) == 0:
            self.tags.append(GLTag(word, self.id, self.image))
            return 1

        tag = self.getTag(word)
        if tag is not None:
            tag.mentioned()
            return 0
        else:
            self.tags.append(GLTag(word, self.id, self.image))
            self.tags.sort(key=lambda x: x.name)
        return 1

    def addTag(self, tag: str, level=None) -> int:
        """ Add a Tag to this image and return the points, depending on the level of the image and whether the Tag is
            new or was already known. If level is none, the actual level of the image is used, add a value to prevent
            changing the level for one user in the middle of his game because of another user.

            :param level: the level the image shall have, either 0, 1 or 2.
            :param tag: Tag to add

            :return points a user gets for this Task
        """
        points = 1
        val = self.validate(tag)

        if val == -1:
            return 0

        lev = self.level if ((level is None) or (level < 0) or (level > 2)) else level

        if lev == 1 and val == 0:
            # a already known tag for a level 1 image gives 2 points
            points = 2
        if lev == 2:
            points = 2

        self.levelUp()
        return points

    def getTag(self, name: str) -> GLTag:
        """ Get a Tag of this image

            :param name: value of this Tag

            :return the Tag, or None if a Tag matching this word doesn't exist
        """
        name = name.lower()
        for tag in self.tags:
            if tag.getWord() == name:
                return tag
        return None

    def printTags(self):
        """ Print the word of each Tag in the list """
        for tag in self.tags:
            print(tag.name, end=" ")
        print()


class GLUser:
    """
    Class representing a user

    Attributes:
        user (User): User instance of the user
        image_current (GLImage): Image this user is currently playing with
        game_mode (int): 0 if user is playing Classic, 1 if Reverse Captcha
        image_level (int): level of this image when user started playing
        tags_for_image_current ([str]): tags he has provided during this round for this image
        cap_captcha (int): if the user is in captcha mode, the position of the main image in the list of images
    """

    def __init__(self, username: str, secret='top-secret'):
        # Todo: is here a try...except needed?
        self.user = User(username, secret)
        db.session.add(self.user)
        db.session.commit()

        self.image_current = GLImage(1)
        self.game_mode = 0
        self.image_level = 0
        self.tags_for_image_current = []
        self.cap_captcha = None

    def getScore(self) -> int:
        """ :return score of the user """
        return self.user.score

    def startClassic(self) -> Image.id:
        """ Start a game in classic mode. Select an image the user has not seen before

            :return the image
        """
        self.game_mode = 0
        self.tags_for_image_current = []

        # get the new image
        iterations = 0
        image_id = None
        new_image = False
        num_images = db.session.query(Image).count()
        while (not new_image) and iterations < num_images:
            image_id = randbelow(num_images) + 1
            try:
                # raises an error, if an image with this id doesn't exist or the user has seen it already
                image = Image.query.get(image_id)
                self.user.seen.append(image)
                db.session.commit()
                new_image = True
            except Exception as e:
                db.session.rollback()
                new_image = False
                image_id = None
                iterations += 1

        # if an image which the user has not seen before couldn't be found, choose a random one
        if image_id is None:
            image_id = randbelow(num_images) + 1
            image = Image.query.get(image_id)

        # create a class for this image
        self.image_current = GLImage(image_id)
        self.image_level = self.image_current.getLevel()
        return self.image_current

    def tagImage(self, tag: str, image=None):
        """ Tag the image with the given Tag, add the reached points to the score

            :param tag: the word to tag
            :param image: GLImage to tag, or none to tag the image this user is playing with
        """
        # if user is playing captcha or has already provided this tag in this round do nothing
        if self.game_mode == 1 or tag in self.tags_for_image_current:
            return

        if image is None:
            image = self.image_current
        self.user.score = self.user.score + image.addTag(tag, self.image_level)
        db.session.commit()

    def startCaptcha(self) -> ([Image.id], [str]):
        """ Start a game in Captcha mode, select one main and n other images, to validate the tags of the main.
            The main is at a random position of the image list.

            :return the images, and the tags to validate
        """
        self.game_mode = 1
        return ([None], [None])

    def capCaptcha(self, cap: int) -> bool:
        """ Validate, whether the user chose the main image, and validate the tags. User gets 10 points, if correct cap.

            :param cap: the image the user chose for this tag

            :return true, if it is the main image, false if not
        """
        # if user is playing classic or this is not the correct cap_captcha return False
        if (self.game_mode != 0) or (cap != self.cap_captcha):
            return False

        # Todo: validate the tags (also if not recognized correctly?)
        self.user.score = self.user.score + 10
        db.session.commit()
        return True

    def end(self) -> int:
        """ end the current game, no matter which game mode.

            :return current score of the user
        """
        return self.user.score

    def skip(self) -> int:
        """ User skips an image, no matter which game mode, then end the game and add a skip to the image table.

            :return score of user
        """
        self.image_current.image.skips = self.image_current.image.skips + 1
        db.session.commit()
        return self.end()
