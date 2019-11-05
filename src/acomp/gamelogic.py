import sqlite3

from spellchecker.spellchecker import SpellChecker

from acomp import db
from acomp.models import Image, Tag, User, user_image, image_tag


class GLTag:
    """
    A class used to represent a single Tag

    Attributes:
        name: string of this Tag (may be multiple words)
        image_id : the id of the image this Tag tags
    """

    def __init__(self, name: str, image_id: int, image=None):
        # add e new tag to the database, if this word never occurred before, or get this tag from the db
        try:
            self.tag = Tag(name)
            db.session.add(self.tag)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.tag = Tag.query.filter_by(name=name).first()

        if image is None:
            try:
                # TODO: check image id
                image = Image.query.get(image_id)
            except Exception as e:
                # TODO: why does this exception occur? should not happen...
                db.session.rollback()
                print('The image could not be found!')
                return

        self.imageID = image_id
        self.image = image
        try:
            image.tags.append(self.tag)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            '''self.mentioned()'''
        self.name = name

    def mentioned(self):
        """
            Increases frequency of Tag for this image by 1
        """
        # enhance the frequency of the tag for this image by one
        '''frequency = image_tag(image_id=self.imageID, tag_id=self.tag.id).frequency
        image_tag.get(image_id=self.imageID, tag_id=self.tag.id).frequency = frequency + 1
        db.session.commit()'''
        pass

    def getFrequency(self) -> int:
        """
            :return frequency of Tag
        """
        '''tags = self.image.tags
        tag = tags.query.filter_by(id=self.tag.id).first()'''
        return 2

    def getWord(self) -> str:
        """ :return word of this Tag """
        return self.name


class GLImage:
    """
        A class used to represent an image

        Attributes:
            id (int): id of the image
            tags ([Tag]): list of all the Tags provided for this image
            forbiddenTags [str]: string list of words which are forbidden to tag if image is in level 2
            level (int): level of this image (corresponds with the amount of provided Tags)
            spellcheck (SpellChecker): instance of the Spellchecker to check the spelling of new Tags
    """

    def __init__(self, id: int):
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
        tagged = len(self.tags)  # TODO: better criteria, e.g. how many user tagged the image
        if tagged > 2:
            self.level = 1
            if tagged > 4:
                self.level = 2
                # TODO: make this better (not alphabetically...)
                for i in range(2):
                    self.forbiddenTags.append(self.tags[i].name)

    def validate(self, word: str) -> int:
        """ Validates the Tag regarding his spelling (minor misspellings are corrected with frequency list algorithm of
            SpellChecker) and forbidden Tag list, if image in level 2.

            :arg word: Tag to validate

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
            self.levelUp()
        return 1

    def addTag(self, tag: str) -> int:
        """ Add a Tag to this image and return the points, depending on the level of the image and whether the Tag is
            new or was already known.

            :arg tag: Tag to add

            :return points a user gets for this Task
        """
        points = 1
        val = self.validate(tag)

        if val == -1:
            return 0

        if self.level == 1 and val == 1:
            # a new tag for a level 2 image gives 2 points
            points = 2
        if self.level == 2:
            points = 2

        return points

    def getTag(self, name: str) -> GLTag:
        """ Get a Tag of this image

            :arg name: value of this Tag

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
    """

    def __init__(self, username: str):
        self.user = User(username, 'top-secret')
        db.session.add(self.user)
        db.session.commit()

    def tagImage(self, image: GLImage, tag: str):
        """ Tag the image with the given Tag, add the reached points to the score

            :arg image: image to tag
            :arg tag: the word to tag
        """
        self.user.score = self.user.score + image.addTag(tag)
        self.user.seen.append(image.image)
        db.session.commit()

    def getScore(self) -> int:
        """ :return score of the user """
        return self.user.score
