class Image:
    def __init__(self, id: int):
        self.id = id
        self.tags = []
        self.forbiddenTags = []
        self.level = 0

    def levelUp(self):
        if len(self.tags) > 2:
            self.level = 1
            if len(self.tags) > 4:
                self.level = 2
                self.forbiddenTags = self.tags[0:2]

    def addTag(self, tag: str) -> int:
        points = 1
        points_level2 = 2
        if len(self.tags) == 0:
            self.tags.append(tag)
        else:
            in_list = False
            for t in self.tags:
                if t == tag:
                    in_list = True
            if not in_list:
                self.tags.append(tag)
                self.levelUp()
            else:
                if self.level == 1:
                    points = 2
                elif self.level == 2 and tag not in self.forbiddenTags:
                    points_level2 = 2
        return points if self.level < 2 else points_level2

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
