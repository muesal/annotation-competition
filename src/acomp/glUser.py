from secrets import randbelow
from flask import url_for, session
from acomp import app, db, sessions
from acomp.models import Image, Tag, User, ImageTag, user_image
from acomp.glImage import GLImage
from json import dumps, loads
from sqlalchemy import func
from time import time


class GLUser:
    """
    Class representing a user

    Attributes:
        user (User): User instance of the user
        game_mode (int): 0 if user is playing Classic, 1 if Reverse Captcha, -1 if he is not playing
        image_id (int): ID of the image this user is currently playing with
        timestamp (int): seconds for last start/end of a game
        image_level (int): level of this image when user started playing
        num_tags (int): number of provided tags (for classic mode)
        cap_captcha (int): if the user is in captcha mode, the position of the main image in the list of images
        joker (int): boolean whether a joker was used or not
        tags ([str]): tags user has provided during this round for this image, or tags of captcha image if captcha mode
        language (str): language the user is playing in
    """

    def __init__(self, id: int, language='en'):
        self.id = id
        self.user = User.query.filter_by(id=id).one_or_none()
        if self.user is None and self.id != -1:
            raise Exception('A user with this ID could not be found. The ID was: {}'.format(id))

        if 'timestamp' not in session or time() - session['timestamp'] > app.config['ACOMP_LIFETIME_USER']:
            session['game_mode'] = -1
            session['image_id'] = 0
            session['timestamp'] = time()
            session['image_level'] = 0
            session['num_tags'] = 0
            session['cap_captcha'] = 0
            session['joker'] = 0
            session['tags'] = '[]'
            session['language'] = language

    def getScore(self) -> int:
        """ :return score of the user """
        return 0 if self.id == -1 else self.user.score

    def getName(self):
        """ :return name of the user """
        print('id: {}'.format(self.id))
        return 'none' if self.id == -1 else self.user.username

    def startClassic(self) -> dict:
        """
        Start a game in classic mode. Select an image the user has not seen before

        :return: the image
        """
        if session['game_mode'] != -1 or self.id == -1:
            self.end()

        session['game_mode'] = 0
        session['num_tags'] = 0
        session['timestamp'] = time()

        # get the new image
        iterations = 0
        image_id = None
        new_image = False

        num_images = db.session.query(Image).count()
        if num_images <= 0:
            raise Exception('No images in DB')

        while (not new_image) and iterations < num_images:
            image_id = randbelow(num_images) + 1
            try:
                # raises an error, if an image with this id doesn't exist or the user has seen it already
                image = Image.query.get(image_id)
                self.user.seen.append(image)
                db.session.commit()
                new_image = True
            except Exception as e:
                app.logger.debug(e)
                db.session.rollback()
                new_image = False
                image_id = None
                iterations += 1

        # if an image which the user has not seen before couldn't be found, choose a random one
        if image_id is None:
            image_id = randbelow(num_images) + 1

        # create a class for this image
        image = Image.query.get(image_id)
        gl_image = GLImage(image_id)
        session['image_id'] = image_id
        session['image_level'] = gl_image.getLevel()

        data: dict = {
            'images': url_for('static', filename='images/' + image.filename),
            'timelimit': app.config['ACOMP_CLASSIC_TIMELIMIT'],
            'forbidden': gl_image.getForbiddenTags(),
            'score': self.getScore(),
            'user': self.user.id
        }
        return data

    def tagImage(self, tag: str, image=None) -> (int, str, int):
        """
        Tag the image with the given Tag, add the reached points to the score
        Return -1 and error message, if an error occurred, else 1 and the tag which was added.

        :param tag: the word to tag
        :param image: GLImage to tag, or none to tag the image this user is playing with

        :return: (validation, message)
        """
        if session['image_id'] == 0:
            raise Exception('No image in DB')
        # if user is playing captcha or has already provided this tag in this round do nothing
        if session['game_mode'] != 0 or self.id == -1:
            raise Exception('Wrong game mode')
        # if the time is up end this game
        if time() - session['timestamp'] > app.config['ACOMP_CLASSIC_TIMELIMIT']:
            self.end()
            return -1, "Your time is over", self.getScore()
        # check if the tagging rate is okay
        session['num_tags'] += 1
        if session['num_tags'] > app.config['ACOMP_CLASSIC_TIMELIMIT'] / 2:
            self.end()
            # TODO: Do something, like deleting previous tags?
            return -1, "your tagging rate was too high, we must suspect you are spam!", self.getScore()
        if tag in loads(session['tags']):
            return -1, "You may not mention this tag again for this image", self.getScore()

        if image is None:
            image = GLImage(session['image_id'])

        try:
            points, tag = image.tag(tag, session['image_level'], language=session['language'])
        except Exception as e:
            return -1, e.args[0], self.getScore()

        tags = loads(session['tags'])
        if tag not in tags:
            tags.append(tag)
            session['tags'] = dumps(tags)
            self.user.score += points
            db.session.commit()
            return 1, tag, self.getScore()
        return -1, "You may not mention this tag again for this image", self.getScore()

    def startCaptcha(self) -> dict:
        """
        Start a game in Captcha mode, select one main and n other images, to validate the tags of the main.
        The main is at a random position of the image list.

        :return: the images, and the tags to validate
        """
        if session['game_mode'] != -1:
            self.end()
        session['game_mode'] = 1
        session['timestamp'] = time()

        num_images = app.config['ACOMP_CAPTCHA_NUM_IMAGES']
        total_images = db.session.query(Image).count()
        if total_images < num_images:
            raise Exception('Not enough images in DB ({} configured for \
                    captcha mode, but only found {})'.format(num_images, total_images))

        session['cap_captcha'] = randbelow(num_images)

        # get the other images random
        rand_images = Image.query.order_by(func.random()).limit(num_images - 1).all()
        images = [None] * num_images
        filenames = [None] * num_images
        ids = []
        i = 0
        for image in rand_images:
            if i == session['cap_captcha']:
                i += 1
            images[i] = image
            filenames[i] = url_for('static', filename='images/' + image.filename)
            ids.append(image.id)
            i += 1

        # cap is a random image which has enough tags
        rand_tagged_images = db.session.query(ImageTag.image_id).group_by(ImageTag.image_id). \
            having(func.count(ImageTag.tag_id) > app.config['ACOMP_CAPTCHA_NUM_TAGS']). \
            order_by(func.random()).limit(num_images)

        # make sure it is different from the other images
        image = Image.query.get(rand_tagged_images.first().image_id)
        while (image.id in ids) and (rand_tagged_images.count() > 1):
            image = Image.query.get(rand_tagged_images.first().image_id)

        session['image_id'] = image.id
        images[session['cap_captcha']] = image
        filenames[session['cap_captcha']] = url_for('static', filename='images/' + image.filename)

        gl_image = GLImage(image.id)
        ids, tags = gl_image.getCaptchaTags(language=session['language'])
        session['tags'] = dumps(ids)

        data: dict = {
            'images': filenames,
            'timelimit': app.config['ACOMP_CLASSIC_TIMELIMIT'],
            'tags': tags,
            'score': self.getScore()
        }
        return data

    def jokerCaptcha(self) -> [int]:
        """
        Fifty-Fifty Joker, remove half of the images which are not the cap, user will only get half of th points.

        :return: list of positions of images, which are not the cap
        """
        if session['game_mode'] != 1:
            raise Exception('Wrong game mode')

        session['joker'] = 1
        rest = (session['cap_captcha'] + 1) % 2
        return [x for x in range(rest, app.config['ACOMP_CAPTCHA_NUM_IMAGES'], 2)]

    def capCaptcha(self, cap: int) -> (int, str, int):
        """
        Validate, whether the user chose the main image, and validate the tags. User gets 10 points, if correct cap.
        Return -1 and error message, if an error occurred, 0 for wrong and 1 for correct captcha.

        :param cap: the image the user chose for this tag

        :return: true, if it is the main image, false if not and the cap
        """
        # if user is playing classic or this is not the correct cap_captcha return False
        if abs(time() - session['timestamp']) > app.config['ACOMP_CAPTCHA_TIMELIMIT']:
            self.end()
            return -1, "Your time is over", self.getScore()
        if session['game_mode'] != 1 or self.id == -1:
            raise Exception('Wrong game mode')

        gl_image = GLImage(session['image_id'])
        if cap != session['cap_captcha']:
            gl_image.verifyTags(loads(session['tags']), False)
            return 0, session['cap_captcha'], self.getScore()

        gl_image.verifyTags(loads(session['tags']), True)
        self.user.score += (10 if session['joker'] == 0 else 5)
        db.session.commit()
        self.end()

        return 1, cap, self.getScore()

    def capEntryQuiz(self, cap: int) -> (int, str):
        """
        Validate, whether the user chose the main image, and validate the tags for the entry quiz.

        :param cap: the image the user chose for this tag

        :return: true, if it is the main image, false if not and the cap
        """
        # if user is playing classic or this is not the correct cap_captcha return False
        if session['game_mode'] != 1 or self.id != -1:
            raise Exception('Wrong game mode')

        return (0 if cap != session['cap_captcha'] else 1), str(session['cap_captcha'])

    def end(self) -> int:
        """
        End the current game, no matter which game mode.

        :return: current score of the user
        """
        session['game_mode'] = -1
        session['image_id'] = 0
        session['image_level'] = 0
        session['num_tags'] = 0
        session['cap_captcha'] = 0
        session['joker'] = 0
        session['tags'] = '[]'
        session['timestamp'] = time()
        return self.getScore()

    def skip(self) -> int:
        """
        User skips an image, no matter which game mode, then end the game and add a skip to the image table.

        :return: score of user
        """
        if session['game_mode'] != -1 and session['image_id'] != 0:
            # else there is no image in database, or user is not playing
            image = Image.query.get(session['image_id'])
            image.skips = image.skips + 1
            db.session.commit()
        return self.end()

    def getHighscore(self) -> dict:
        """
        Get the high score of points over all users in the database.

        :return: dictionary with list of the top users (username, score)
        """
        sorted_by_score = User.query.order_by(User.score.desc()).limit(app.config['ACOMP_NUM_HIGHSCORE'])
        highscores = []
        for user in sorted_by_score:
            highscores.append((user.username, user.score))
        app.logger.debug(highscores)

        images = Image.query.count()
        users = User.query.count()
        tags = Tag.query.count()

        data: dict = {
            'highscores': highscores,
            'user': (self.getName(), self.getScore()),
            'users': users,
            'images': images,
            'tags': tags,
        }
        return data
