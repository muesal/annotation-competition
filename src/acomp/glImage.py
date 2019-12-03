from spellchecker.spellchecker import SpellChecker
from secrets import randbelow
from acomp import app, db
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

    def getForbiddenTags(self) -> [str]:
        self.levelUp()
        return self.forbiddenTags

    def getCaptchaTags(self) -> [str]:
        captcha_tags = []
        all_tags = ImageTag.query.filter_by(image_id=self.id).all()
        num_tags = app.config['ACOMP_CAPTCHA_NUM_TAGS']

        # if there are less ore exactly as many tags for this image, as wanted, just take them all.
        if num_tags <= db.session.query(all_tags).count():
            for elem in all_tags:
                captcha_tags.append(Tag.query.filter_by(id=elem.tag_id).one_and_only().name)
                elem.total_verified = elem.total_verified + 1
            return captcha_tags

        '''
        # else choose tags with very complex and thoughtful algorithm
        # half of the tags have been shown to a user before, but not been verified correctly at max.
        not_successful_verified = all_tags.query.filter(ImageTag.successful_verified == 0,
                                                        ImageTag.total_verified > 0).all()
        i = 0
        for elem in not_successful_verified:
            captcha_tags.append(Tag.query.filter_by(id=elem.tag_id).one_and_only().name)
            elem.total_verified = elem.total_verified + 1
            i += 1
            if i >= num_tags / 2:
                break
        '''

        # choose random entries, until we have enough tags
        while len(captcha_tags) < num_tags:
            rand = randbelow(db.session.query(all_tags).count())
            tag_id = db.session.query(all_tags)[rand].tag_id
            captcha_tags.append(Tag.query.filter_by(id=tag_id).one_and_only().name)
            tag_image = all_tags.query.filter_by(tag_id=tag_id).one_and_only()
            tag_image.total_verified = tag_image.total_verified + 1

        return captcha_tags

    def verifyTags(self, tags: [str]):
        for tag in tags:
            gl_tag = GLTag(tag, self.id, self.image)
            image_tag = ImageTag.query.filter_by(image_id=self.id, tag_id=gl_tag.id).one_or_none()
            image_tag.successful_verified = image_tag.successful_verified + 1
            try:
                db.session.commit()
            except Exception as e:
                app.logger.debug(e)
                db.session.rollback()
