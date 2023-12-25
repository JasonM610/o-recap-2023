from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("--headless=new")


playcount_present = EC.presence_of_element_located(
    (By.XPATH, "//div[@class='beatmap-playcount']")
)
button_present = EC.presence_of_element_located(
    (By.XPATH, "//button[normalize-space()='show more']")
)


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

    driver = webdriver.Chrome(options=options)
    driver.get(user_url)

    # scroll to "Historical" and wait for profile to load
    historical = driver.find_element(By.XPATH, "//div[@data-page-id='historical']")
    historical.location_once_scrolled_into_view

    try:
        WebDriverWait(driver, 20).until(playcount_present)

        # press "Show More" until all beatmaps are loaded
        while True:
            try:
                show_more_button = WebDriverWait(driver, 20).until(button_present)
                show_more_button.send_keys("\n")
            except TimeoutException:
                break
    except TimeoutException:
        pass

    # build list of beatmap IDs once map playcounts have been expanded
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
