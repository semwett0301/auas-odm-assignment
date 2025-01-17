CREATE TABLE IF NOT EXISTS movie (
    meta_link VARCHAR(512) PRIMARY KEY,
    title VARCHAR(256),
    release_date DATE,
    metascore NUMERIC,
    userscore NUMERIC,
    duration INTEGER,
    movie_url VARCHAR(256),
    mpaa VARCHAR(256),
    budget NUMERIC,
    opening_weekend NUMERIC
);

CREATE TABLE IF NOT EXISTS movie_parents_summary (
    movie_meta_link VARCHAR PRIMARY KEY REFERENCES movie(meta_link),
    sex_and_nudity varchar,
    violence varchar,
    frightening varchar,
    alcho varchar,
    profanity varchar
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
    type VARCHAR(256),
    PRIMARY KEY (movie_meta_link, company_name)
);

CREATE TABLE IF NOT EXISTS region (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS region_income (
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    region_name VARCHAR REFERENCES region(name),
    releases_amount INTEGER,
    gross NUMERIC,
    rank INTEGER,
    PRIMARY KEY (movie_meta_link, region_name)
);

CREATE TABLE IF NOT EXISTS person (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_cast (
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    person_name VARCHAR REFERENCES person(name),
    position VARCHAR(256),
    role VARCHAR(256),
    PRIMARY KEY (movie_meta_link, person_name)
);

CREATE TABLE IF NOT EXISTS release (
    release_id SERIAL PRIMARY KEY,
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    date DATE,
    domestic_income NUMERIC,
    international_income NUMERIC,
    worldwide_income NUMERIC
);

CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    movie_meta_link VARCHAR REFERENCES movie(meta_link),
    score NUMERIC,
    body TEXT,
    date DATE,
    author VARCHAR
);
