from acomp import db
from acomp.models import Image, Tag, User, ImageTag, user_image


class GLTag:
    """
    A class used to represent a single Tag

    Attributes:
        name (str): string of this Tag (may be multiple words)
        imageID (int): the id of the image this Tag tags
        image (Image): the image this Tag tags
        tag (Tag): this Tag
    """

    def __init__(self, name: str, image_id: int, image=None):
        # add e new tag to the database, if this word never occurred before, or get this tag from the db

        self.tag = Tag.query.filter_by(name=name).one_or_none()
        if self.tag is None:
            try:
                self.tag = Tag(name)
                db.session.add(self.tag)
                db.session.commit()
            except Exception as e: #TODO: SQLException instead of any
                # The tag is already known to the db
                print(e, '\n')
                db.session.rollback()

        self.id = self.tag.id
        if image is None:
            try:
                # TODO: check image id
                image = Image.query.get(image_id)
            except Exception as e:
                # TODO: why does this exception occur? should not happen...
                db.session.rollback()
                print('The image could not be found! Error: ')
                print(e, end='\n\n')
                return

        self.imageID = image_id
        self.image = image
        try:
            it = ImageTag(image_id=self.imageID, tag_id=self.id, frequency=1, successful_verified=0, total_verified=0)
            it.tag = self.tag
            it.image = self.image
            db.session.commit()
        except Exception as e:
            # The tag and this image are already connected, the frequency has to be increased with mentioned()
            db.session.rollback()
            self.mentioned()
        self.name = name

    def mentioned(self):
        """
            Increases frequency of Tag for this image by 1
        """
        it = ImageTag.query.filter_by(
            tag_id=self.id, image_id=self.imageID).one_or_none()
        it.frequency = it.frequency + 1

    def getFrequency(self) -> int:
        """
            :return frequency of Tag
        """
        frequency = ImageTag.query.filter_by(
            tag_id=self.id, image_id=self.imageID).one_or_none().frequency
        return frequency

    def getWord(self) -> str:
        """ :return word of this Tag """
        return self.name
