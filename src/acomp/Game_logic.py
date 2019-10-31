from spellchecker import SpellChecker


class Tag:
    """
    A class used to represent a single Tag

    Attributes:
        word: string of this Tag (may be multiple words)
        image_id : the id of the image this Tag tags
        frequency: how often this Tag was mentioned for this image
    """

    def __init__(self, word: str, image_id: int):
        self.word = word
        self.imageID = image_id
        self.frequency = 1

    def mentioned(self):
        """ Increases frequency of Tag by 1 """
        self.frequency += 1

    def getFrequency(self) -> int:
        """ :return frequency of Tag """
        return self.frequency

    def getWord(self) -> str:
        """ :return word of this Tag """
        return self.word


class Image:
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
        self.id = id
        self.tags = []
        self.forbiddenTags = []
        self.level = 0
        self.spellcheck = SpellChecker(distance=1)

    def levelUp(self):
        """ Increase the level of the Image if necessary TODO: increase not with number of Tags but by how many user tagged the image """
        if len(self.tags) > 2:
            self.level = 1
            if len(self.tags) > 4:
                self.level = 2
                for i in range(2):
                    self.forbiddenTags.append(self.tags[i].word)

    def validate(self, word: str) -> int:
        """ Validates the Tag regarding his spelling (minor misspellings are corrected with frequency list algorithm of
            SpellChecker) and forbidden Tag list, if image in level 2.

            :arg word: Tag to validate

            :return -1 if invalid, else position of the Tag in self.tags
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

        # Tag is valid add Tag or increase its frequency, return
        if len(self.tags) == 0:
            self.tags.append(Tag(word, self.id))
            return 0
        for i in range(len(self.tags)):
            if self.tags[i].word == word:
                self.tags[i].mentioned()
                return i
        self.tags.append(Tag(word, self.id))
        self.tags.sort(key=lambda x: x.word)
        self.levelUp()
        return len(self.tags) - 1

    def addTag(self, tag: str) -> int:
        """ Add a Tag to this image and return the points, depending on the level of the image and whether the Tag is
            new or was already known.

            :arg tag: Tag to add

            :return points a user gets for this Task
        """
        points = 1
        lastTag = len(self.tags) - 1
        val = self.validate(tag)

        if val < 0:
            return 0

        if self.level == 1:
            if val <= lastTag:
                # it is a new tag, since it's pos is behind the former last tag
                points = 2
        if self.level == 2:
            points = 2

        return points

    def getTag(self, word: str) -> Tag:
        """ Get a Tag of this image

            :arg word: value of this Tag

            :return the Tag, or None if a Tag matching this word doesn't exist
        """
        word = word.lower()
        for tag in self.tags:
            if tag.word == word:
                return tag
        return None

    def printTags(self):
        """ Print the word of each Tag in the list """
        for tag in self.tags:
            print(tag.word, end=" ")
        print()


class User:
    """
    Class representing a user

    Attributes:
        id (int): id of the user
        score (int): the score of the user
    """

    def __init__(self, id: int):
        self.id = id
        self.score = 0

    def tagImage(self, image: Image, tag: str):
        """ Tag the image with the given Tag, add the reached points to the score

            :arg image: image to tag
            :arg tag: the Tag
        """
        self.score = self.score + image.addTag(tag)

    def getScore(self) -> int:
        """ :return score of the user """
        return self.score


if __name__ == "__main__":
    user = User(0)
    image = Image(0)
    user.tagImage(image, 'stupide')
    user.tagImage(image, 'stupide')
    user.tagImage(image, 'stupido')
    user.tagImage(image, 'stupida')
    user.tagImage(image, 'stupida')
    print("points of user: {}".format(user.getScore()))
    image.printTags()
    print("level of image: {}".format(image.level))
