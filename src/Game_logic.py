from spellchecker import SpellChecker


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
                self.forbiddenTags = self.tags[0:2]

    def validate(self, tag: str) -> int:
        wrong = self.spellcheck.unknown([tag])
        if len(wrong) > 0:
            corrected = self.spellcheck.correction(tag)
            if corrected == tag:
                return -1
            tag = corrected

        if len(self.tags) == 0:
            self.tags.append(tag)
            return 0
        for i in range(len(self.tags)):
            if self.tags[i] == tag:
                return i
        self.tags.append(tag)
        self.tags.sort()
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
            points = 2 if tag not in self.forbiddenTags else 0

        return points

    def printTags(self):
        for tag in self.tags:
            print(tag, end=" ")
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
