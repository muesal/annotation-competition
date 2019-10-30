from spellchecker import SpellChecker


class Tag:
    def __init__(self, word: str, image_id: int):
        self.word = word
        self.imageID = image_id
        self.frequency = 1

    def mentioned(self):
        self.frequency += 1

    def getFrequency(self) -> int:
        return self.frequency

    def getWord(self) -> str:
        return self.word


class Image:
    def __init__(self, id: int):
        self.id = id
        self.tags = []
        self.forbiddenTags = []
        self.level = 0
        self.spellcheck = SpellChecker(distance=1)

    def levelUp(self):
        if len(self.tags) > 2:
            self.level = 1
            if len(self.tags) > 4:
                self.level = 2
                for i in range(2):
                    self.forbiddenTags.append(self.tags[i].word)

    def validate(self, word: str) -> int:
        wrong = self.spellcheck.unknown([word])
        if len(wrong) > 0:
            corrected = self.spellcheck.correction(word)
            if corrected == word:
                return -1
            word = corrected

        if self.level == 2 and word in self.forbiddenTags:
            return -1

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
        points = 1
        lastTag = len(self.tags) - 1
        val = self.validate(tag)

        if val < 0:
            return 0

        if self.level == 1:
            if val <= lastTag:
                points = 2
        if self.level == 2:
            points = 2

        return points

    def getTag(self, word: str) -> Tag:
        for tag in self.tags:
            if tag.word == word:
                return tag
        return None

    def printTags(self):
        for tag in self.tags:
            print(tag.word, end=" ")
        print()


class User:
    def __init__(self, id: int):
        self.id = id
        self.score = 0

    def tagImage(self, image: Image, tag: str):
        self.score = self.score + image.addTag(tag)

    def getScore(self) -> int:
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
