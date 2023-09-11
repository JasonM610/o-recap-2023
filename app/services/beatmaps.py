import time
from typing import Union
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


base_url = "https://osu.ppy.sh/u"
beatmap_list = []
driver = webdriver.Chrome()


def get_all_beatmaps() -> list[int]:
    """
    Builds list of ranked and loved beatmaps. Sourced from https://osu.respektive.pw/beatmaps.
    If used, this will be called for users that have played a lot of beatmaps (25,000+)

    Returns:
        list[int]: A list of all ranked and loved beatmap IDs
    """

    return beatmap_list


def get_beatmaps_from_profile(user: Union[int, str]) -> list[int]:
    """
    Builds list of beatmaps user played by scraping "Most Played" section on userpage.
    Note the "Most Played" section isn't perfectly accurate (some maps go missing), but this method saves time compared to checking for a score on every map

    Args:
        user (Union[int, str]): The user's ID or name. Keeping this flexible for now but may change with implementation later

    Returns:
        list[int]: A list of beatmaps played by the user
    """
    user_url = f"{base_url}/{user}"
    driver.get(user_url)

    # scroll to "Historical" and wait for data
    historical = driver.find_element(By.XPATH, "//div[@data-page-id='historical']")
    historical.location_once_scrolled_into_view
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='beatmap-playcount']"))
    )

    # press "Show More" button until all beatmaps are loaded
    st = time.time()
    while True:
        try:
            button_present = EC.presence_of_element_located(
                (By.XPATH, "//button[normalize-space()='show more']")
            )
            WebDriverWait(driver, 10).until(button_present)

            # currently presses all buttons on page (such as best performances, beatmaps)
            # doesn't slow things down but would prefer a direct approach
            show_more_button = historical.find_element(
                By.XPATH, "//button[normalize-space()='show more']"
            )
            show_more_button.send_keys("\n")

            time.sleep(1)
        except TimeoutException:
            break

    element_list = driver.find_elements(By.XPATH, "//div[@class='beatmap-playcount']")

    beatmap_list = [
        ele.find_element(By.CLASS_NAME, "beatmap-playcount__cover")
        .get_attribute("href")
        .split("/")[-1]
        for ele in element_list
    ]

    print(beatmap_list)
    print(len(beatmap_list), time.time() - st)

    return beatmap_list


get_beatmaps_from_profile("waddlelad")
