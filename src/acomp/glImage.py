from spellchecker.spellchecker import SpellChecker
from acomp import app, db, tl, wl
from acomp.models import Image, Tag, User, ImageTag, user_image
from nltk import pos_tag
from nltk.corpus import wordnet
from sqlalchemy import func


class GLImage:
    """
    A class used to represent an image

    Attributes:
        image (Image): the image
        id (int): id of the image
        forbiddenTags ([str]): string list of words which are forbidden to tag if image is in level 2
        level (int): level of this image (corresponds with the amount of provided Tags)
    """

    def __init__(self, id: int):
        if id < 1:
            id = 1
        self.image = Image.query.get(id)
        if self.image is None:
            raise Exception('A Image with this ID could not be found. The ID was: {}'.format(id))
        self.id = id
        self.forbiddenTags = []
        self.level = 0

    def levelUp(self):
        """ Increase the level of the Image if necessary """
        query_image_user = User.query.join(user_image).join(Image).filter(
            user_image.c.image_id == self.id).all()
        tagged = len(query_image_user)
        if tagged > app.config['ACOMP_NUM_LEV1']:
            self.level = 1
        if tagged > app.config['ACOMP_NUM_LEV2']:
            self.level = 2
            self.forbiddenTags = []
            tags = ImageTag.query.filter_by(image_id=self.id).order_by(ImageTag.frequency.desc()).limit(
                app.config['ACOMP_CAPTCHA_NUM_TAGS']).all()
            for i in range(app.config['ACOMP_CAPTCHA_NUM_TAGS']):
                tag = Tag.query.filter_by(id=tags[i].tag_id).one_or_none()
                self.forbiddenTags.append(tag.name)

    def getLevel(self) -> int:
        """ :return: the level of the image """
        self.levelUp()
        return self.level

    def translateTags(self, tags: [str], src_language: str, dest_language: str) -> [str]:
        """
        Translate a list of tags from the src_language to the dest_language.

        :param tags: a list of strings to translate
        :param src_language: the language of the tags (google code)
        :param dest_language: language to translate to (google code)

        :return: list of the translated tags
        """
        if src_language != dest_language:
            translation = tl.translate(tags, src=src_language, dest=dest_language)
            for i in range(len(tags)):
                tags[i] = translation[i].text
        return tags

    def getForbiddenTags(self, language='en') -> [str]:
        """
        Get the tags which are forbidden for this image.

        :param language: language the tags should be in

        :return: list of the tags in the given language
        """
        self.levelUp()
        return self.translateTags(self.forbiddenTags, 'en', language)

    def lemmatizeTag(self, tag: [str], origin_tag: str) -> (str, str):
        """
        Check whether the words are spelled correctly, auto-correct them if possible. Get their Part-of-Speech and stem
        it them to the root form. Verbs will be put a to in front, adverbs are only allowed in combination with an verb.

        :param tag: the tag
        :param origin_tag: the tag the user gave, e.g. a german expression of the tag

        :return: the correct tag and it's root synonym
        """
        sc = SpellChecker(distance=1)

        # if unknown to dictionary: correct if minor error, else Tag is invalid
        for i in range(len(tag)):
            wrong = list(sc.unknown([tag[i]]))
            if len(wrong) > 0:
                tag[i] = sc.correction(wrong[0])
                if tag[i] == wrong[0]:
                    raise Exception("\'{}\' could not be found in our dictionary.".format(origin_tag))

        pos = pos_tag(tag)

        to = ''
        # todo: switch case?
        if pos[0][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            # noun, e.g. house
            pos_one = 'n'
        elif pos[0][1] in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            # verb, e.g. to go
            pos_one = 'v'
            to = 'to '
        elif pos[0][1] in ['JJ', 'JJR', 'JJS']:
            # adjective, e.g. red
            pos_one = 'a'
        elif pos[0][1] in ['RB', 'RBR', 'RBS']:
            # adverb, e.g. silently
            pos_one = 'r'
        else:
            raise Exception("Your tag has to bee either a noun, verb or adjective. If \'{}\' is of these part-of-speech"
                            ", try to reformulate it (e.g. looking instead of look)".format(origin_tag))

        correct_tag = to + wl.lemmatize(tag[0], pos=pos_one)

        # if the tag consists of only one word, look for it's main synonym (e.g. large for big):
        if len(tag) == 1:
            syns = wordnet.synsets(correct_tag, pos=pos_one)
            return correct_tag, correct_tag if len(syns) == 0 else syns[0].lemmas()[0].name()

        pos_two = None
        if pos_one == 'n' and pos[1][1] in ['NN', 'NNS', 'NNP', 'NNPS']:
            # e.g. Sherlock Holmes
            pos_two = 'n'
        elif pos_one == 'v':
            if pos[1][1] in ['RB', 'RBR', 'RBS']:
                # e.g. to walk silently
                pos_two = 'r'
            if pos[1][1] in ['RP', 'IN']:
                # eg. to give up or to look after; these words should not be lemmatized
                pos_two = None
        else:
            raise Exception("Our natural language processor supposes you meant {} {}. "
                            "\'{}\'({}) in combination with \'{}\'({}) does not make sense to it. "
                            "Try to reformulate it (e.g. looking after instead of look after). "
                            "If you think we're wrong please contact us."
                            .format(tag[0], tag[1], tag[1], pos, tag[0], pos_one))
        correct_tag += ' ' + (wl.lemmatize(tag[1], pos=pos_two) if pos_two is not None else tag[1])
        # don't look for synonyms if the tag consists of more than one word
        return correct_tag, correct_tag

    def validate(self, tag: str, level, language='en') -> (int, str):
        """
        Validates the Tag regarding his spelling (minor misspellings are corrected with frequency list algorithm of
        SpellChecker) and forbidden Tag list, if image in level 2.

        :param tag: Tag to validate
        :param level: the level of the image
        :param language:language of the tag (google code)

        :raise exception, if more than two words, not in dictionary, or in forbidden tags.

        :return: 0 if the tag was already known, 1 if he is valid and new for this picture
        """
        # translate the word to english
        word = self.translateTags([tag], language, 'en')[0]

        # word should not consist of more than two words (except if it starts with 'to', e.g. 'to go down')
        word = word.lower().split(" ")
        if word[0] == 'to':
            word.pop(0)
        if len(word) > 2:
            raise Exception("A tag may not be longer than two words.")

        # lemmatize it
        word, syn = self.lemmatizeTag(word, tag)

        # invalid if image is level 2 and Tag is forbidden
        if level == 2 and syn in self.forbiddenTags:
            raise Exception("'{}' and synonyms have been mentioned very often for this image, we cannot give you points"
                            " for this.\n(Not allowed tags may be seen above, under \'mentioned Tags\'; their synonyms"
                            " are not allowed as well)".format(tag))

        # Tag is valid: add Tag or increase its frequency, return 0 if the tag was already known, 1 otherwise
        return self.addTag(word), self.translateTags([word], 'en', language)[0]

    def tag(self, tag: str, level=None, language='en') -> (int, str):
        """
        Add a Tag to this image and return the points, depending on the level of the image and whether the Tag is
        new or was already known. If level is none, the actual level of the image is used, add a value to prevent
        changing the level for one user in the middle of his game because of another user.

        :param tag: Tag to add
        :param level: the level the image shall have, either 0, 1 or 2.
        :param language:language of the tag (google code)

        :return: points a user gets for this Task
        """
        lev = self.level if ((level is None) or (level < 0) or (level > 2)) else level

        points = 1
        val, tag = self.validate(tag, lev, language)

        if lev == 1 and val == 0:
            # a already known tag for a level 1 image gives 2 points
            points = 2
        if lev == 2:
            points = 2

        return points, tag

    def hasTag(self, name: str) -> int:
        """
        Get a Tag of this image

        :param name: value of this Tag

        :return: 0 if a Tag matching this word doesn't exist for this image or 1 if it does
        """
        name = name.lower()
        # make sure, this tag does exist
        tag = Tag.query.filter_by(name=name).one_or_none()
        if tag is None:
            return 0

        # make sure it is connected with this image
        return 0 if ImageTag.query.filter_by(tag_id=tag.id, image_id=self.id).one_or_none() is None else 1

    def tooGeneric(self, tag_id: int) -> bool:
        """
        Check whether this tag is too generic to be valid.

        :param tag_id: id of the tag
        :return: true if it is to generic
        """
        num_images = Image.query.count()
        num_tag = ImageTag.query.filter_by(tag_id=tag_id).count()
        return num_tag/num_images > app.config['ACOMP_CLASSIC_RATIO']

    def addTag(self, name: str) -> int:
        """
        Add this tag to the database if it never occurred before.
        Else get it from the db and either connect it with the image ore increase its frequency.

        :param tag: the tag to add to this image

        :return: 0 if a Tag matching this word didn't exist for this image or 1 if it did
        """
        tag = Tag.query.filter_by(name=name).one_or_none()
        if tag is None:
            try:
                tag = Tag(name)
                db.session.add(tag)
                db.session.commit()
            except Exception:  # TODO: SQLException instead of any
                # The tag is already known to the db
                db.session.rollback()

        known = 0
        try:
            it = ImageTag(image_id=self.id, tag_id=tag.id, frequency=1, successful_verified=0, total_verified=0)
            it.tag = tag
            it.image = self.image
            db.session.commit()
        except Exception:
            # The tag and this image are already connected, the frequency has to be increased with mentioned()
            db.session.rollback()
            if self.tooGeneric(tag.id):
                raise Exception("'{}' is too generic, as it was mentioned for more than {}% of our images."
                                .format(name, app.config['ACOMP_CLASSIC_RATIO']))
            known = 1
            it = ImageTag.query.filter_by(tag_id=tag.id, image_id=self.id).one_or_none()
            it.frequency = it.frequency + 1
        return known

    def getCaptchaTags(self, language='en') -> ([int], [str]):
        """
        Get some tags describing this image for the Captcha game-mode. Tha tags are chosen randomly.

        :param language: language the tags should be in

        :return: list of id of the tags, list of the tags in the requested language
        """
        captcha_ids = []
        captcha_tags = []
        num_tags = app.config['ACOMP_CAPTCHA_NUM_TAGS']
        random_tags = ImageTag.query.filter_by(image_id=self.id).order_by(func.random()).limit(num_tags).all()

        # return the random tags (acomp_captcha_num_tags or the number of tags this image is connected with)
        for elem in random_tags:
            captcha_ids.append(elem.tag_id)
            captcha_tags.append(Tag.query.filter_by(id=elem.tag_id).one_or_none().name)
            elem.total_verified = elem.total_verified + 1
        return captcha_ids, self.translateTags(captcha_tags, 'en', language)

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

    def verifyTags(self, tags: [str], correct: bool):
        """
        Verify the captcha tags based on whether the user chose the correct image or not.

        :param tags: the ids of the tags the user validated
        :param correct: boolean whether
        """
        for id in tags:
            image_tag = ImageTag.query.filter_by(image_id=self.id, tag_id=id).one_or_none()
            image_tag.total_verified += 1
            if correct:
                image_tag.successful_verified += 1
            try:
                db.session.commit()
            except Exception as e:
                app.logger.debug(e)
                db.session.rollback()
