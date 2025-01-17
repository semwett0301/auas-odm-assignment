# Lucas Boeseman
# This is the script that prepares and inserts the scrapped data into database

import re
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from settings import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_URL, POSTGRES_PORT, \
    POSTGRES_DB
from utils import read_jsonl


def prepare_metacritic(metacritic_df):
    metacritic_df['release_date'] = metacritic_df['release_date'].apply(lambda x: datetime.strptime(x, "%b %d, %Y"))

    def convert_duration(duration_str):
        hours, minutes = 0, 0
        if 'h' in duration_str:
            hours = int(duration_str.split('h')[0].strip())
        if 'm' in duration_str:
            minutes = int(duration_str.split('m')[0].split()[-1].strip())
        return hours * 60 + minutes

    metacritic_df['duration'] = metacritic_df['duration'].apply(convert_duration)

    return metacritic_df.drop(['genres', 'cast', 'title'], axis=1)


def prepare_genres(metacritic_df):
    unique_genres = metacritic_df['genres'].explode().unique()
    genres_meta_link = metacritic_df[['meta_link', 'genres']].explode('genres', ignore_index=True)

    genres_meta_link['movie_meta_link'] = genres_meta_link['meta_link']
    genres_meta_link['genre_name'] = genres_meta_link['genres']

    return unique_genres, genres_meta_link.drop(['meta_link', 'genres'], axis=1)


def prepare_releases(box_office_df):
    df_exploded = box_office_df.explode('releases', ignore_index=True)

    releases_df = pd.json_normalize(df_exploded['releases'])
    releases_df = pd.concat([df_exploded[['box_office_link']], releases_df], axis=1)
    releases_df['date'] = releases_df['date'].apply(prepare_date)

    releases_df['domestic_income'] = releases_df['domestic_income'].map(remove_dollar)
    releases_df['international_income'] = releases_df['international_income'].map(remove_dollar)
    releases_df['worldwide_income'] = releases_df['worldwide_income'].map(remove_dollar)

    return releases_df


def prepare_regions(box_office_df):
    df_exploded = box_office_df.explode('region_incomes', ignore_index=True)
    region_incomes_df = pd.json_normalize(df_exploded['region_incomes'])

    regions_df = pd.concat([df_exploded[['box_office_link']], region_incomes_df], axis=1)
    regions_df['gross'] = regions_df['gross'].apply(remove_dollar)

    return regions_df['name'].unique(), regions_df.dropna().drop(['name'], axis=1)


def prepare_date(date):
    date_match = re.match(r"([a-zA-Z]+ \d{1,2}, \d{4})", date)
    return pd.to_datetime(date_match.group(0), format='%B %d, %Y')


def prepare_cast(df, merger):
    df_exploded = df.explode('cast', ignore_index=True)

    cast_df = pd.json_normalize(df_exploded['cast'])
    df_cast_merged = pd.concat([df_exploded[merger], cast_df], axis=1)

    unique_names_df = df_cast_merged[['name']].drop_duplicates().reset_index(drop=True)
    df_cast_merged['person_name'] = df_cast_merged['name']

    return unique_names_df, df_cast_merged.drop(['name'], axis=1)


def prepare_urls(df, urls):
    for url in urls:
        df[url] = df[url].apply(
            lambda x: x.split('?')[0] if not x.split('?')[0].endswith('/') else x.split('?')[0][:-1])

    return df


def remove_dollar(price):
    return int(price.replace('$', '').replace(',', ''))


def prepare_box_office(box_office_df):
    box_office_df['opening_weekend'] = box_office_df['opening_weekend'].apply(remove_dollar)
    box_office_df = box_office_df.drop(['cast', 'region_incomes', 'releases'], axis=1)

    return box_office_df


def prepare_parents_guide(imdb_df):
    parents_guide = imdb_df["parents_guide"]

    df = pd.DataFrame({
        "sex_and_nudity": parents_guide.apply(lambda x: x.get("sex_and_nudity")),
        "violence": parents_guide.apply(lambda x: x.get("violence")),
        "frightening": parents_guide.apply(lambda x: x.get("frightening")),
        "alcho": parents_guide.apply(lambda x: x.get("alcohol")),
        "profanity": parents_guide.apply(lambda x: x.get("profanity")),
        "meta_link": imdb_df["meta_link"]
    })

    df['movie_meta_link'] = imdb_df['meta_link']

    return df.drop(['meta_link'], axis=1)


def prepare_reviews(imdb_df):
    df_exploded = imdb_df.explode('reviews', ignore_index=True)

    reviews_df = pd.json_normalize(df_exploded['reviews'])
    reviews_df = pd.concat([df_exploded[['meta_link']], reviews_df], axis=1)
    reviews_df['movie_meta_link'] = reviews_df['meta_link']
    reviews_df['date'] = reviews_df['date'].apply(lambda x: datetime.strptime(x, "%b %d, %Y"))
    reviews_df['score'] = reviews_df['score'].apply(lambda x: int(x) if x else np.nan)

    return reviews_df.drop(['meta_link'], axis=1)


def prepare_companies(imdb_df):
    df_exploded = imdb_df.explode('companies', ignore_index=True)

    companies_df = pd.json_normalize(df_exploded['companies'])
    companies_df = pd.concat([df_exploded[['meta_link']], companies_df], axis=1)

    companies_df['movie_meta_link'] = companies_df['meta_link']
    companies_df['company_name'] = companies_df['name']

    return companies_df['name'].unique(), companies_df.drop(['meta_link', 'name'], axis=1)


def prepare_imdb(imdb_df):
    imdb_df['release_date'] = imdb_df['release_date'].apply(lambda x: datetime.strptime(x.split(" (")[0], "%B %d, %Y"))

    return imdb_df.drop(['genres', 'reviews', 'parents_guide', 'companies'], axis=1)


def gather_movies(box_office_raw_data, metacritic_raw_data, imdb_raw_data):
    merged_1_2 = pd.merge(imdb_raw_data, metacritic_raw_data, on="meta_link", how="inner")
    final_merged = pd.merge(merged_1_2, box_office_raw_data, on="box_office_link", how="inner")

    final_merged['release_date_x'] = pd.to_datetime(final_merged['release_date_x'])
    final_merged['release_date_y'] = pd.to_datetime(final_merged['release_date_y'])

    final_merged["release_date"] = final_merged[["release_date_x", "release_date_y"]].max(axis=1)

    return final_merged.drop(['release_date_x', 'release_date_y'], axis=1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Put the args")
        sys.exit(1)

    engine = create_engine(
        f"postgresql+pg8000://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_URL}:{POSTGRES_PORT}/{POSTGRES_DB}")

    file_paths = sys.argv[1:]

    metacritic_raw_data = prepare_urls(read_jsonl(file_paths[0]), ['meta_link'])
    imdb_movie_raw_data = prepare_urls(read_jsonl(file_paths[1]), ['meta_link', 'box_office_link'])
    box_office_raw_data = prepare_urls(read_jsonl(file_paths[2]), ['box_office_link'])

    meta_unique_genres, meta_genres_meta_link = prepare_genres(metacritic_raw_data)

    metacritic_raw_data = prepare_metacritic(metacritic_raw_data)

    box_cast_names_df, box_cast_merged = prepare_cast(box_office_raw_data, 'box_office_link')
    unique_regions, regions_df = prepare_regions(box_office_raw_data)
    releases_df = prepare_releases(box_office_raw_data)

    box_office_raw_data = prepare_box_office(box_office_raw_data)

    imdb_unique_genres, imdb_genres_meta_link = prepare_genres(imdb_movie_raw_data)
    imdb_unique_companies, imdb_companies_meta_link = prepare_companies(imdb_movie_raw_data)
    parents_guide_df = prepare_parents_guide(imdb_movie_raw_data)
    reviews_df = prepare_reviews(imdb_movie_raw_data)

    imdb_movie_raw_data = prepare_imdb(imdb_movie_raw_data)

    result_movie_df = gather_movies(box_office_raw_data, metacritic_raw_data, imdb_movie_raw_data)
    joined_unique_genres = list(set(imdb_unique_genres.tolist() + meta_unique_genres.tolist()))

    result_movie_df.drop(['box_office_link'], axis=1).to_sql('movie', con=engine, if_exists='append', index=False)

    pd.DataFrame({'name': joined_unique_genres}).to_sql('genre', con=engine, if_exists='append', index=False)
    pd.DataFrame({'name': unique_regions[~pd.isna(unique_regions)]}).to_sql('region', con=engine, if_exists='append', index=False)
    pd.DataFrame({'name': imdb_unique_companies}).to_sql('company', con=engine, if_exists='append', index=False)
    box_cast_names_df.to_sql('person', con=engine, if_exists='append', index=False)

    releases_df = pd.merge(releases_df, result_movie_df, on="box_office_link", how="inner").drop(
        result_movie_df.columns.drop("meta_link"), axis=1)
    releases_df['movie_meta_link'] = releases_df['meta_link']
    releases_df.drop(["meta_link"], axis=1).to_sql('release', con=engine, if_exists='append', index=False)

    pd.merge(imdb_companies_meta_link, result_movie_df, left_on="movie_meta_link", right_on="meta_link",
             how="inner").drop(result_movie_df.columns, axis=1).drop_duplicates(['movie_meta_link', 'company_name']).to_sql('movie_company', con=engine, if_exists='append',
                                                                       index=False)
    pd.merge(meta_genres_meta_link, result_movie_df, left_on="movie_meta_link", right_on="meta_link", how="inner").drop(
        result_movie_df.columns, axis=1).to_sql('movie_genre', con=engine, if_exists='append',
                                                index=False)

    cast = pd.merge(box_cast_merged, result_movie_df, left_on="box_office_link", right_on="box_office_link",
                    how="inner")
    cast['movie_meta_link'] = cast['meta_link']
    cast.drop(result_movie_df.columns, axis=1).drop_duplicates(['movie_meta_link', 'person_name']).to_sql('movie_cast',
                                                                                                          con=engine,
                                                                                                          if_exists='append',
                                                                                                          index=False)

    regions = pd.merge(regions_df, result_movie_df, left_on="box_office_link", right_on="box_office_link",
                       how="inner").fillna(np.nan)
    regions['movie_meta_link'] = regions['meta_link']
    regions.drop(result_movie_df.columns, axis=1).drop_duplicates(['movie_meta_link', 'region_name']).to_sql(
        'region_income', con=engine, if_exists='append', index=False)

    pd.merge(reviews_df, result_movie_df, left_on="movie_meta_link", right_on="meta_link", how="inner").drop(
        result_movie_df.columns, axis=1).to_sql('review', con=engine, if_exists='append', index=False)

    pd.merge(parents_guide_df, result_movie_df, left_on="movie_meta_link", right_on="meta_link", how="inner").drop(
        result_movie_df.columns, axis=1).to_sql('movie_parents_summary', con=engine, if_exists='append', index=False)
