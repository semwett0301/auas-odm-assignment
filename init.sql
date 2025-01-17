CREATE TABLE IF NOT EXISTS movie (
    meta_link VARCHAR(512) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    release_date DATE NOT NULL,
    metascore NUMERIC NOT NULL,
    userscore NUMERIC NOT NULL,
    duration INTEGER NOT NULL,
    movie_url VARCHAR(256) NOT NULL,
    mpaa VARCHAR(256) NOT NULL,
    budget NUMERIC NOT NULL,
    opening_weekend NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS movie_parents_summary (
    movie_meta_link VARCHAR PRIMARY KEY REFERENCES movie(meta_link),
    sex_and_nudity varchar NOT NULL,
    violence varchar NOT NULL,
    frightening varchar NOT NULL,
    alcho varchar NOT NULL,
    profanity varchar NOT NULL
);

CREATE TABLE IF NOT EXISTS genre (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_genre (
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    genre_name VARCHAR REFERENCES genre(name),
    PRIMARY KEY (movie_meta_link, genre_name)
);

CREATE TABLE IF NOT EXISTS company (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_company (
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    company_name VARCHAR REFERENCES company(name),
    type VARCHAR(256) NOT NULL,
    PRIMARY KEY (movie_meta_link, company_name)
);

CREATE TABLE IF NOT EXISTS region (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS region_income (
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    region_name VARCHAR REFERENCES region(name),
    releases_amount INTEGER NOT NULL,
    gross NUMERIC NOT NULL,
    rank INTEGER NOT NULL,
    PRIMARY KEY (movie_meta_link, region_name)
);

CREATE TABLE IF NOT EXISTS person (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_cast (
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    person_name VARCHAR REFERENCES person(name),
    position VARCHAR(256) NOT NULL,
    role VARCHAR(256) NOT NULL,
    PRIMARY KEY (movie_meta_link, person_name)
);

CREATE TABLE IF NOT EXISTS release (
    release_id SERIAL PRIMARY KEY,
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    date DATE NOT NULL,
    domestic_income NUMERIC NOT NULL,
    international_income NUMERIC NOT NULL,
    worldwide_income NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    score NUMERIC,
    body TEXT,
    date DATE NOT NULL,
    author VARCHAR NOT NULL
);
