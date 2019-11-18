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
                    # self.forbiddenTags.append(self.tags[i].name)

    def getLevel(self) -> int:
        """ :return the level of the image"""
        self.levelUp()
        return self.level

    def validate(self, word: str) -> (int, str):
        """ Validates the Tag regarding his spelling (minor misspellings are corrected with frequency list algorithm of
            SpellChecker) and forbidden Tag list, if image in level 2.

            :param word: Tag to validate

            :raise exception, if more than two words, not in dictionary, or in forbidden tags.

            :return 0 if the tag was already known, 1 if he is valid and new for this picture
        """
        # word should not consist of more than two words
        word = word.split(" ")
        if len(word) > 2:
            raise Exception("A tag may not be longer than two words.")
        # Todo: only letters, and '-'

        # for each word in tag: if unknown to dictionary: correct if minor error, else Tag is invalid
        wrong = list(self.spellcheck.unknown(word))
        if len(wrong) > 0:
            for i in range(len(wrong)):
                word[i] = self.spellcheck.correction(wrong[i])
                if word[i] == wrong[i]:
                    raise Exception("This word(s) could not be found in our dictionary.")

        # should be one string again
        word = (' '.join(word)).lower()

        # invalid if image is level 2 and Tag is forbidden
        if self.level == 2 and word in self.forbiddenTags:
            raise Exception("This tag has been mentioned very often, we cannot give you points for this."
                            "\n(Not allowed tags may be seen on the right side, under \'mentioned Tags\')")

        # Tag is valid: add Tag or increase its frequency, return 0 if the tag was already known, 1 otherwise
        tag = self.getTag(word)
        if tag is not None:
            tag.mentioned()
            return 0, word
        else:
            self.tags.append(GLTag(word, self.id, self.image))
            self.tags.sort(key=lambda x: x.name)
        return 1, word

    def addTag(self, tag: str, level=None) -> (int, str):
        """ Add a Tag to this image and return the points, depending on the level of the image and whether the Tag is
            new or was already known. If level is none, the actual level of the image is used, add a value to prevent
            changing the level for one user in the middle of his game because of another user.

            :param level: the level the image shall have, either 0, 1 or 2.
            :param tag: Tag to add

            :return points a user gets for this Task
        """
        points = 1
        val, tag = self.validate(tag)

        lev = self.level if ((level is None) or (level < 0) or (level > 2)) else level

        if lev == 1 and val == 0:
            # a already known tag for a level 1 image gives 2 points
            points = 2
        if lev == 2:
            points = 2

        self.levelUp()
        return points, tag

    def getTag(self, name: str) -> GLTag:
        """ Get a Tag of this image

            :param name: value of this Tag

            :return the Tag, or None if a Tag matching this word doesn't exist
        """
        name = name.lower()
        # make sure, this tag does exist
        tag = Tag.query.filter_by(name=name).one_or_none()
        if tag is None:
            return None

        # make sure it is connected with this image
        if ImageTag.query.filter_by(tag_id=tag.id, image_id=self.id).one_or_none() is None:
            return None

        # put it in own list of tags
        if len(self.tags) >= 0:
            for tag in self.tags:
                if tag.getWord() == name:
                    return tag

        self.tags.append(GLTag(name, self.id, self.image))
        return self.tags[-1]

    def printTags(self):
        """ Print the word of each Tag in the list """
        for tag in self.tags:
            print(tag.name, end=" ")
        print()
