from spellchecker.spellchecker import SpellChecker
from secrets import randbelow
from acomp import app, db
from acomp.models import Image, Tag, User, ImageTag, user_image
from acomp.glTag import GLTag
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from googletrans import Translator


class GLImage:
    """
        A class used to represent an image

        Attributes:
            image (Image); the image
            id (int): id of the image
            tags ([Tag]): list of all the Tags provided for this image
            forbiddenTags [str]: string list of words which are forbidden to tag if image is in level 2
            level (int): level of this image (corresponds with the amount of provided Tags)
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

    def levelUp(self):
        """ Increase the level of the Image if necessary """
        query_image_user = User.query.join(user_image).join(Image).filter(
            user_image.c.image_id == self.id).all()
        tagged = len(query_image_user)
        if tagged > 2:
            self.level = 1
            if tagged > 4:
                self.level = 2
                tags = ImageTag.query.filter_by(image_id=self.id).first()
                sorted_by_frequency = tags.query.order_by(ImageTag.frequency.desc()).all()
                for i in range(app.config['ACOMP_CAPTCHA_NUM_TAGS']):
                    tag = Tag.query.filter_by(id=sorted_by_frequency[i].tag_id).one_or_none()
                    self.forbiddenTags.append(tag.name)

    def getLevel(self) -> int:
        """ :return the level of the image"""
        self.levelUp()
        return self.level

    def lemmatizeTag(self, tag: [str], origin_tag: str) -> str:
        """
        Check whether the words are spelled correctly, auto-correct them if possible. Get their Part-of-Speech and stem
        it them to the root form. Verbs will be put a to in front, adverbs are only allowed in combination with an verb.

        :param tag: the tag
        :param origin_tag: the tag the user gave, e.g. a german expression of the tag
        :return: the correct tag
        """
        sc = SpellChecker(distance=1)
        wl = WordNetLemmatizer()

        word = tag[0]

        # if unknown to dictionary: correct if minor error, else Tag is invalid
        wrong = list(sc.unknown([word]))
        if len(wrong) > 0:
            word = sc.correction(wrong[0])
            if word == wrong[0]:
                raise Exception("\'{}\' could not be found in our dictionary.".format(origin_tag))

        pos = pos_tag([word])[0][1]
        to = ''
        # todo: switch case?
        if pos in ['NN', 'NNS', 'NNP', 'NNPS']:
            # noun, e.g. house
            pos_one = 'n'
        elif pos in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            # verb, e.g. to go
            pos_one = 'v'
            to = 'to '
        elif pos in ['JJ', 'JJR', 'JJS']:
            # adjective, e.g. red
            pos_one = 'a'
        elif pos in ['RB', 'RBR', 'RBS']:
            # adverb, e.g. silently
            pos_one = 'r'
        else:
            # todo: find an example for a adjective which was misscaluated as noun
            raise Exception("Your tag has to bee either a noun, verb or adjective. If \'{}\' is of these part-of-speech"
                            ", try to reformulate it (e.g. looking instead of look)".format(origin_tag))

        correct_tag = to + wl.lemmatize(word, pos=pos_one)

        # if the tag consists of two words repeat:
        if len(tag) > 1:
            word = tag[1]
            # if unknown to dictionary: correct if minor error, else Tag is invalid
            wrong = list(sc.unknown([word]))
            if len(wrong) > 0:
                word = sc.correction(wrong[0])
                if word == wrong[0]:
                    raise Exception("\'{}\' could not be found in our dictionary.".format(origin_tag))

            pos = pos_tag([word])
            pos_two = None
            if pos_one == 'n' and pos in ['NN', 'NNS', 'NNP', 'NNPS']:
                # e.g. Sherlock Holmes
                pos_two = 'n'
            elif pos_one == 'v':
                if pos in ['RB', 'RBR', 'RBS']:
                    # e.g. to walk silently
                    pos_two = 'r'
                if pos in ['RP', 'IN']:
                    # eg. to give up or to look after; these words should not be lemmatized
                    pos_two = None
            else:
                pos_two = pos
                raise Exception("Our natural language processor supposes you meant {} {}. "
                                "\'{}\'({}) in combination with \'{}\'({}) does not make sense to it. "
                                "Try to reformulate it (e.g. looking after instead of look after). "
                                "If you think we're wrong please contact us."
                                .format(tag[0], word, word, pos_two, tag[0], pos_one))
            correct_tag += ' ' + (wl.lemmatize(word, pos=pos_two) if pos_two is not None else word)

        return correct_tag

    def translateTags(self, tags: [str], src_language: str, dest_language: str) -> [str]:
        """
        Translate a list of tags from the src_language to the dest_language.

        :param tags: a list of strings to translate
        :param src_language: the language of the tags (google code)
        :param dest_language: language to translate to (google code)

        :return: list of the translated tags
        """
        if src_language != dest_language:
            tl = Translator()
            for i in range(len(tags)):
                tags[i] = tl.translate(tags[i], src=src_language, dest=dest_language).text
        return tags

    def validate(self, tag: str, language='en') -> (int, str):
        """ Validates the Tag regarding his spelling (minor misspellings are corrected with frequency list algorithm of
            SpellChecker) and forbidden Tag list, if image in level 2.

            :param tag: Tag to validate
            :param language:language of the tag (google code)

            :raise exception, if more than two words, not in dictionary, or in forbidden tags.

            :return 0 if the tag was already known, 1 if he is valid and new for this picture
        """
        # TODO: check the language code
        # translate the word to english
        word = self.translateTags([tag], language, 'en')[0]

        # word should not consist of more than two words (except if it starts with 'to', e.g. 'to go down')
        word = word.lower().split(" ")
        if word[0] == 'to':
            word.pop(0)
        if len(word) > 2:
            raise Exception("A tag may not be longer than two words.")

        # lemmatize it
        word = self.lemmatizeTag(word, tag)

        # invalid if image is level 2 and Tag is forbidden
        if self.level == 2 and word in self.forbiddenTags:
            # TODO: are the mentioned tags on the right side?
            raise Exception("'{}' has been mentioned very often for this image, we cannot give you points for this."
                            "\n(Not allowed tags may be seen on the right side, under \'mentioned Tags\')".format(tag))

        # Tag is valid: add Tag or increase its frequency, return 0 if the tag was already known, 1 otherwise
        known = self.getTag(word)
        if known is not None:
            known.mentioned()
            return 0, self.translateTags([word], 'en', language)[0]
        else:
            self.tags.append(GLTag(word, self.id, self.image))
            self.tags.sort(key=lambda x: x.name)
        return 1, self.translateTags([word], 'en', language)[0]

    def addTag(self, tag: str, level=None, language='en') -> (int, str):
        """ Add a Tag to this image and return the points, depending on the level of the image and whether the Tag is
            new or was already known. If level is none, the actual level of the image is used, add a value to prevent
            changing the level for one user in the middle of his game because of another user.

            :param tag: Tag to add
            :param level: the level the image shall have, either 0, 1 or 2.
            :param language:language of the tag (google code)

            :return points a user gets for this Task
        """
        points = 1
        val, tag = self.validate(tag, language)

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

    def getForbiddenTags(self, language='en') -> [str]:
        self.levelUp()
        return self.translateTags(self.forbiddenTags, 'en', language)

    def getCaptchaTags(self, language='en') -> [str]:
        captcha_tags = []
        all_tags = ImageTag.query.filter_by(image_id=self.id).all()
        num_tags = app.config['ACOMP_CAPTCHA_NUM_TAGS']

        # if there are less or exactly as many tags for this image as wanted, just take them all.
        if num_tags <= db.session.query(all_tags).count():
            for elem in all_tags:
                captcha_tags.append(Tag.query.filter_by(id=elem.tag_id).one_and_only().name)
                elem.total_verified = elem.total_verified + 1
            return self.translateTags(captcha_tags, 'en', language)

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

        return self.translateTags(captcha_tags, 'en', language)

    def verifyTags(self, tags: [str], correct: bool, language='en'):
        tags = self.translateTags(tags, 'en', language)
        # TODO: this translation may lead to words we do not have in our database -> solution?
        for tag in tags:
            gl_tag = GLTag(tag, self.id, self.image)
            image_tag = ImageTag.query.filter_by(image_id=self.id, tag_id=gl_tag.id).one_or_none()
            image_tag.total_verified += 1
            if correct:
                image_tag.successful_verified += 1
            try:
                db.session.commit()
            except Exception as e:
                app.logger.debug(e)
                db.session.rollback()
