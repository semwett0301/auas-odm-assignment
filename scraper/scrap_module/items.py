from scrapy import Item, Field


class ImdbUrlItem(Item):
    url = Field()

class ImdbMovieItem(Item):
    title = Field()
    genres = Field()
    release_date = Field()
    reviews = Field()
    meta_link = Field()
    budget = Field()
    parents_guide = Field()
    companies = Field()

class ImdbParentsGuide(Item):
    sex_and_nudity = Field()
    violance = Field()
    frightening = Field()
    alcho = Field()
    profanity = Field()

class ImdbOrganization(Item):
    name = Field()
    type = Field()

class ImdbReview(Item):
    score = Field()
    date = Field()
    author = Field()
    body = Field()

class MetacriticMovie(Item):
    title = Field()
    release_date = Field()
    metascore = Field()
    userscore = Field()
    duration = Field()
    genres = Field()
    mpaa = Field()
    cast = Field()
    meta_link = Field()
    movie_url = Field()

class MetacriticReview(ImdbReview):
    type = Field()

class MetacriticCast(Item):
    name = Field()
    position = Field()
    role = Field()
