class Article:
    def __init__(self, item):
        self.title: str = item.find("title")
        self.description: str = item.find("description")
        self.date: str = item.find("pubDate")
