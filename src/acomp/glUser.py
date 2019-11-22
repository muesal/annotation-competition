from secrets import randbelow
from flask import url_for
from acomp import app, db
from acomp.models import Image, Tag, User, ImageTag, user_image
from acomp.glImage import GLImage
import time


class GLUser:
    """
    Class representing a user

    Attributes:
        user (User): User instance of the user
        image_current (GLImage): Image this user is currently playing with
        game_mode (int): 0 if user is playing Classic, 1 if Reverse Captcha, -1 if he is not playing
        image_level (int): level of this image when user started playing
        tags_for_image_current ([str]): tags he has provided during this round for this image
        cap_captcha (int): if the user is in captcha mode, the position of the main image in the list of images
    """

    def __init__(self, id: int):
        self.user = User.query.filter_by(id=id).one_or_none()

        if self.user is None:
            raise Exception('A user with this ID could not be found. The ID was: {}'.format(id))

        # TODO: nicer way
        if db.session.query(Image).count() <= 0:
            app.logger('There are no images in our database')
        else:
            self.image_current = GLImage(1)

        self.game_mode = -1
        self.image_level = 0
        self.tags_for_image_current = []
        self.cap_captcha = None
        self.timestamp = time.time()

    def getScore(self) -> int:
        """ :return score of the user """
        return self.user.score

    def startClassic(self) -> dict:
        """ Start a game in classic mode. Select an image the user has not seen before

            :return the image
        """
        self.game_mode = 0
        self.tags_for_image_current = []
        self.timestamp = time.time()

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
                db.session.rollback()
                new_image = False
                image_id = None
                iterations += 1

        # if an image which the user has not seen before couldn't be found, choose a random one
        if image_id is None:
            image_id = randbelow(num_images) + 1

        # create a class for this image
        image = Image.query.get(image_id)
        self.image_current = GLImage(image_id)
        self.image_current.levelUp()
        self.image_level = self.image_current.getLevel()

        data: dict = {'images': url_for('static', filename='images/' + image.filename),
                      'timelimit': app.config['ACOMP_CLASSIC_TIMELIMIT'],
                      'accepted': self.image_current.getForbiddenTags(),
                      'score': self.getScore,
                      'user': self.user.id}
        return data

    def tagImage(self, tag: str, image=None) -> (int, str):
        """ Tag the image with the given Tag, add the reached points to the score
            Return -1 and error message, if an error occurred, else 0 and the tag which was added.
            Return 1 if the game is over (time's up)

            :param tag: the word to tag
            :param image: GLImage to tag, or none to tag the image this user is playing with

            :returns (validation, message)
        """
        if self.image_current is None:
            raise Exception('No image in DB')
        # if user is playing captcha or has already provided this tag in this round do nothing
        if self.game_mode != 0:
            raise Exception('Wrong game mode')
        if tag in self.tags_for_image_current:
            return -1, "You already provided this tag for this image"
        # if the time is up end this game
        if abs(time.time() - self.timestamp) > app.config['ACOMP_CLASSIC_TIMELIMIT']:
            self.end()
            return 1, "{}".format(self.user.score)

        if image is None:
            image = self.image_current

        points, tag = image.addTag(tag, self.image_level)

        self.tags_for_image_current.append(tag)
        self.user.score = self.user.score + points
        db.session.commit()
        return 0, tag

    def startCaptcha(self) -> dict:
        """ Start a game in Captcha mode, select one main and n other images, to validate the tags of the main.
            The main is at a random position of the image list.

            :return the images, and the tags to validate
        """
        self.game_mode = 1
        self.timestamp = time.time()
        data: dict
        {}
        '''data: dict = {'images': url_for('static', filename='images/' + image.filename),
                      'timelimit': app.config['ACOMP_CLASSIC_TIMELIMIT'],
                      'tags': self.image_current.getCaptchaTags(),
                      'score': self.score}'''
        return data

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
        self.game_mode = -1
        self.image_level = 0
        self.tags_for_image_current = []
        self.cap_captcha = None
        self.timestamp = time.time()
        return self.user.score

    def skip(self) -> int:
        """ User skips an image, no matter which game mode, then end the game and add a skip to the image table.

            :return score of user
        """
        if self.game_mode != -1 and self.image_current.image is not None:
            # else there is no image in database, or user is not playing
            self.image_current.image.skips = self.image_current.image.skips + 1
            db.session.commit()
        return self.end()
