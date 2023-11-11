import time
import polars as pl
from typing import List
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def collect_beatmap_ids(user_id: int, beatmaps_played: int) -> List[int]:
    return (
        collect_ids_from_profile(user_id)
        if beatmaps_played <= 25000
        else collect_all_ids()
    )


def collect_ids_from_profile(user_id: int) -> List[int]:
    """
    Scrapes "Most Played" section on the userpage to build a list of all beatmaps a user has played
    Note that some maps (< 1%) go missing, and more go missing for users that have played a lot of maps

    Args:
        user_id (int): A user's ID

    Returns:
        List[int]: A list of beatmap IDs from maps played by the user
    """
    user_url = f"https://osu.ppy.sh/users/{user_id}"
    driver = webdriver.Chrome()
    driver.get(user_url)

    playcount_present = EC.presence_of_element_located(
        (By.XPATH, "//div[@class='beatmap-playcount']")
    )
    button_present = EC.presence_of_element_located(
        (By.XPATH, "//button[normalize-space()='show more']")
    )

    # scroll to "Historical" and wait for data
    historical = driver.find_element(By.XPATH, "//div[@data-page-id='historical']")
    historical.location_once_scrolled_into_view
    WebDriverWait(driver, 10).until(playcount_present)

    # press "Show More" button until all beatmaps are loaded
    while True:
        try:
            WebDriverWait(driver, 10).until(button_present)

            show_more_button = historical.find_element(
                By.XPATH, "//button[normalize-space()='show more']"
            )
            show_more_button.send_keys("\n")

            time.sleep(1)
        except TimeoutException:
            break

    # compare speed to current implementation:
    # element_list = driver.find_elements(By.XPATH, "//a[@class='beatmap-playcount__cover']")
    # beatmap_urls = [ele.get_attribute("href") for ele in element_list]

    get_beatmap_urls = "return Array.from(document.querySelectorAll('.beatmap-playcount__cover')).map(element => element.getAttribute('href'));"
    beatmap_urls = driver.execute_script(get_beatmap_urls)
    beatmap_ids = [int(url.split("/")[-1]) for url in beatmap_urls]

    driver.quit()

    return beatmap_ids


def collect_all_ids() -> List[int]:
    """
    Builds list of ranked and loved beatmaps. Sourced from https://osu.respektive.pw/beatmaps.
    This is called for users that have played a lot of beatmaps (25,000+)

    Returns:
        List[int]: A list of all ranked and loved beatmap IDs
    """

    pass
