CREATE TABLE IF NOT EXISTS movie (
    key_title_year VARCHAR(512) PRIMARY KEY,
    metascore NUMERIC,
    userscore NUMERIC,
    imdb_rating NUMERIC,
    duration INTEGER,
    movie_url VARCHAR(256),
    mpaa NUMERIC,
    budget NUMERIC,
    is_colored BOOLEAN,
    opening_weekend NUMERIC
);

CREATE TABLE IF NOT EXISTS movie_parents_summary (
    movie_key_title VARCHAR PRIMARY KEY REFERENCES movie(key_title_year),
    sex_and_nudity NUMERIC,
    violence NUMERIC,
    frightening NUMERIC,
    alcho NUMERIC,
    profanity NUMERIC
);

CREATE TABLE IF NOT EXISTS genre (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_genre (
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    genre_name VARCHAR REFERENCES genre(name),
    PRIMARY KEY (movie_key_title, genre_name)
);

CREATE TABLE IF NOT EXISTS company (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_company (
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    company_name VARCHAR REFERENCES company(name),
    type VARCHAR,
    PRIMARY KEY (movie_key_title, company_name)
);

CREATE TABLE IF NOT EXISTS region (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS region_income (
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    region_name VARCHAR REFERENCES region(name),
    releases_amount INTEGER,
    gross NUMERIC,
    rank INTEGER,
    PRIMARY KEY (movie_key_title, region_name)
);

CREATE TABLE IF NOT EXISTS person (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movie_cast (
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    person_name VARCHAR REFERENCES person(name),
    position VARCHAR,
    role VARCHAR,
    PRIMARY KEY (movie_key_title, person_name)
);

CREATE TABLE IF NOT EXISTS release (
    release_id SERIAL PRIMARY KEY,
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    release_group_name VARCHAR,
    date DATE,
    markets_amount INTEGER,
    domestic_income NUMERIC,
    international_income NUMERIC,
    worldwide_income NUMERIC
);

CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    type VARCHAR,
    score NUMERIC,
    body TEXT,
    date DATE,
    author VARCHAR
);

CREATE TABLE IF NOT EXISTS streaming_platform (
    name VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS streaming_option (
    movie_key_title VARCHAR REFERENCES movie(key_title_year),
    streaming_platform_name VARCHAR REFERENCES streaming_platform(name),
    price NUMERIC,
    PRIMARY KEY (movie_key_title, streaming_platform_name)
);
