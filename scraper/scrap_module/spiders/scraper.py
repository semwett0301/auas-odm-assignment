import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Path to your ChromeDriver
driver_path = r"C:\Users\LucasvanderWielenAlp\OneDrive - Alpine Hearing Protection\Documenten\Master DDB\ODM\chromedriver-win64\chromedriver.exe"
service = Service(driver_path)

try:
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 20)  # Wait timeout set to 20 seconds

    # Navigate to the movie page
    driver.get("https://www.imdb.com/title/tt0111161/")
    
    # Handle popups
    try:
        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]')))
        close_button.click()
        print("Popup dismissed.")
    except TimeoutException:
        print("No popup appeared.")

    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
        cookie_button.click()
        print("Cookie popup dismissed.")
    except TimeoutException:
        print("No cookie popup appeared.")

    # Scrape movie title
    title = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@data-testid="hero__primary-text"]'))).text
    print(f"Title: {title}")

    # 1. Extract Director without clicking (review this)
    try:
        director_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[@class="ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link" and contains(@href, "/name/") and contains(@href, "_dr_1")]')
            )
        )
        director = director_element.text
    except TimeoutException:
        director = "N/A"
    print(f"Director: {director}")

    # Extract Genres
    genre_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="ipc-chip-list__scroller"]/a')))
    genres = [genre.text for genre in genre_elements]
    print(f"Genres: {', '.join(genres)}")

    # Extract Certificate (review this)
    try:
        certificate_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//li[.//span[text()="Certificate"]]/div/ul/li/span'))
        )
        certificate = certificate_element.text
    except TimeoutException:
        certificate = "N/A"
    print(f"Certificate: {certificate}")

    # Extract Release Date
    try:
        release_date = wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "releaseinfo") and contains(@class, "ipc-metadata-list-item__list-content-item--link")]'))).text
        print(f"Release Date: {release_date}")
    except TimeoutException:
        release_date = "N/A"
        print("Release Date not found.")

    # Navigate to "Full Cast & Crew" page and scrape cast
    cast_page_link = wait.until(EC.presence_of_element_located((By.XPATH, '//a[@aria-label="See full cast and crew"]'))).get_attribute('href')
    driver.get(cast_page_link)

    cast_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//table[contains(@class, "cast_list")]//tr')))
    cast = []
    for row in cast_elements:
        try:
            actor_name = row.find_element(By.XPATH, './td[2]/a').text.strip()
            character_name = row.find_element(By.XPATH, './td[4]').text.strip()
            cast.append({"actor": actor_name, "character": character_name})
        except NoSuchElementException:
            continue  # Skip rows that don't match the expected structure

    print(f"Total cast members scraped: {len(cast)}")
    for member in cast:
        print(f"{member['actor']} as {member['character']}")

    # Navigate to reviews page
    driver.get("https://www.imdb.com/title/tt0111161/reviews/")

    # Scrape reviews
    scores = [s.text for s in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@class="ipc-rating-star--rating"]')))]
    review_bodies = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="ipc-html-content-inner-div"]')))]
    dates = [d.text for d in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//li[@class="ipc-inline-list__item review-date"]')))]
    authors = [a.text for a in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@data-testid="author-link"]')))]

    # Ensure all lists are of the same length
    num_reviews = min(len(scores), len(review_bodies), len(dates), len(authors))
    reviews = [{"score": scores[i], "date": dates[i], "author": authors[i], "review": review_bodies[i]} for i in range(num_reviews)]

    print(f"Total reviews scraped: {num_reviews}")
    for review in reviews:
        print(f"Score: {review['score']}, Date: {review['date']}, Author: {review['author']}, Review: {review['review']}")

finally:
    driver.quit() 
