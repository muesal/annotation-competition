from secrets import randbelow
from flask import url_for, session
from acomp import app, db, sessions
from acomp.models import Image, Tag, User, ImageTag, user_image
from acomp.glImage import GLImage
import time
from json import dumps, loads


class GLUser:
    """
    Class representing a user

    Attributes:
        user (User): User instance of the user
        game_mode (int): 0 if user is playing Classic, 1 if Reverse Captcha, -1 if he is not playing
        timestamp (int): seconds for last start/end of a game
        image_id (int): ID of the image this user is currently playing with
        image_level (int): level of this image when user started playing
        num_levels (int): number of provided tags (for classic mode)
        cap_captcha (int): if the user is in captcha mode, the position of the main image in the list of images
        tags ([str]): tags user has provided during this round for this image, or tags of captcha image if captcha mode
    """

    def __init__(self, id: int, language='en'):
        self.user = User.query.filter_by(id=id).one_or_none()

        if self.user is None:
            raise Exception('A user with this ID could not be found. The ID was: {}'.format(id))

        # TODO: nicer way
        if db.session.query(Image).count() <= 0:
            app.logger('There are no images in our database')

        if 'game_mode' not in session:
            session['game_mode'] = -1
        if 'image_id' not in session:
            session['image_id'] = 0
        if 'timestamp' not in session:
            session['timestamp'] = time.time()
        if 'image_level' not in session:
            session['image_level'] = 0
        if 'num_tags' not in session:
            session['num_tags'] = 0
        if 'cap_captcha' not in session:
            session['cap_captcha'] = 0
        if 'tags' not in session:
            session['tags'] = '[]'
        if 'languge' not in session:
            session['language'] = language

    def getScore(self) -> int:
        """ :return score of the user """
        return self.user.score

    def startClassic(self) -> dict:
        """
        Start a game in classic mode. Select an image the user has not seen before

        :return: the image
        """
        session['game_mode'] = 0
        session['num_tags'] = 0
        session['timestamp'] = time.time()

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
        gl_image.levelUp()
        session['image_id'] = image_id
        session['image_level'] = gl_image.getLevel()
        session['tags'] = dumps(gl_image.getForbiddenTags())

        data: dict = {
            'images': url_for('static', filename='images/' + image.filename),
            'timelimit': app.config['ACOMP_CLASSIC_TIMELIMIT'],
            'accepted': session['tags'],
            'score': self.getScore(),
            'user': self.user.id
        }
        return data

    def tagImage(self, tag: str, image=None) -> (int, str):
        """
        Tag the image with the given Tag, add the reached points to the score
        Return -1 and error message, if an error occurred, else 1 and the tag which was added.
        Return -2 if the game is over (time's up)

        :param tag: the word to tag
        :param image: GLImage to tag, or none to tag the image this user is playing with

        :return: (validation, message)
        """
        if session['image_id'] == 0:
            raise Exception('No image in DB')
        # if user is playing captcha or has already provided this tag in this round do nothing
        if session['game_mode'] != 0:
            raise Exception('Wrong game mode')
        # if the time is up end this game
        if abs(time.time() - session['timestamp']) > app.config['ACOMP_CLASSIC_TIMELIMIT']:
            self.end()
            return -2, "{}".format(self.user.score)
        # check if the tagging rate is okay
        session['num_tags'] += 1
        if session['num_tags'] > app.config['ACOMP_CLASSIC_TIMELIMIT'] / 2:
            self.end()
            # TODO: Do something, like deleting previous tags?
            return -1, "your tagging rate was too high, we must suspect you are spam!"
        if tag in loads(session['tags']):
            return -1, "You may not mention this tag again for this image"

        if image is None:
            image = GLImage(session['image_id'])

        try:
            points, tag = image.addTag(tag, session['image_level'], language=session['language'])
        except Exception as e:
            return -1, e.args[0]

        tags = loads(session['tags'])
        if tag not in tags:
            tags.append(tag)
            session['tags'] = dumps(tags)

            self.user.score += points
            db.session.commit()
            return 1, tag
        return -1, "You may not mention this tag again for this image"

    def startCaptcha(self) -> dict:
        """
        Start a game in Captcha mode, select one main and n other images, to validate the tags of the main.
        The main is at a random position of the image list.

        :return: the images, and the tags to validate
        """
        session['game_mode'] = 1
        session['timestamp'] = time.time()

        num_images = db.session.query(Image).count()
        if num_images <= 0:
            raise Exception('No images in DB')

        # get n random images
        images = []
        filenames = []
        for i in range(app.config['ACOMP_CAPTCHA_NUM_IMAGES']):
            image_id = randbelow(num_images) + 1
            images.append(Image.query.get(image_id))
            filenames.append(url_for('static', filename='images/' + images[i].filename))

        # cap is a random one of these images
        session['cap_captcha'] = randbelow(app.config['ACOMP_CAPTCHA_NUM_IMAGES'])

        i = 0
        # count how many tags this image is connected with
        image = images[session['cap_captcha']]
        image_tags = ImageTag.query.filter_by(image_id=image.id).all()
        num_image_tags = db.session.query(image_tags).count()

        # get an image for cap, which has more than three tags, if possible
        while num_image_tags < app.config['ACOMP_CAPTCHA_NUM_TAGS'] and i < num_images:
            # get a random image_id
            image_id = randbelow(num_images) + 1
            image = Image.query.get(image_id)
            # count how many tags the image is connected with
            image_tags = ImageTag.query.filter_by(image_id=image_id).all()
            num_image_tags = db.session.query(image_tags).count()

        session['image_id'] = image.id
        images[session['cap_captcha']] = image
        filenames[session['cap_captcha']] = url_for('static', filename='images/' + image.filename)
        gl_image = GLImage(image.id)

        session['tags'] = dumps(gl_image.getCaptchaTags(language=session['language']))
        data: dict = {'images': filenames,
                      'timelimit': app.config['ACOMP_CLASSIC_TIMELIMIT'],
                      'tags': session['tags'],
                      'score': self.getScore()}
        return data

    def capCaptcha(self, cap: int) -> (int, str):
        """
        Validate, whether the user chose the main image, and validate the tags. User gets 10 points, if correct cap.
        Return -1 and error message, if an error occurred, 0 for wrong and 1 for correct captcha.
        Return -2 if the game is over (time's up)

        :param cap: the image the user chose for this tag

        :return: true, if it is the main image, false if not
        """
        # if user is playing classic or this is not the correct cap_captcha return False
        if abs(time.time() - session['timestamp']) > app.config['ACOMP_CLASSIC_TIMELIMIT']:
            self.end()
            return -2, "{}".format(self.user.score)
        if session['game_mode'] != 1:
            raise Exception('Wrong game mode')

        gl_image = GLImage(session['image_id'])
        if cap != session['cap_captcha']:
            gl_image.verifyTags(loads(session['tags']), False, language=session['language'])
            return 0, 'image {} is not the fitting image'.format(cap)

        gl_image.verifyTags(loads(session['tags']), True, language=session['language'])
        self.user.score = self.user.score + 10
        db.session.commit()

        return 1, '{}'.format(self.user.score)

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
        session['tags'] = '[]'
        session['timestamp'] = time.time()
        return self.user.score

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
        sorted_by_score = User.query.order_by(User.score.desc()).all()
        highscores = []
        for i in range(app.config['ACOMP_NUM_HIGHSCORE']):
            highscores.append((sorted_by_score[i].name, sorted_by_score[i].score))
        hs_as_jsn = dumps(highscores)
        data: dict = {'highscores': hs_as_jsn}
        return data
