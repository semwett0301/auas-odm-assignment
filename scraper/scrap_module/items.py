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
    box_office_link = Field()
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

class Cast(Item):
    name = Field()
    position = Field()
    role = Field()

class BoxOfficeMovie(Item):
    box_office_link = Field()
    opening_weekend = Field()
    region_incomes = Field()
    releases = Field()
    cast = Field()

class BoxOfficeRegionIncome(Item):
    name = Field()
    releases_amount = Field()
    gross = Field()
    rank = Field()

class BoxOfficeRelease(Item):
    date = Field()
    domestic_income = Field()
    international_income = Field()
    worldwide_income = Field()