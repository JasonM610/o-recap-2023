from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

base_url = "https://osu.ppy.sh/u"
driver = webdriver.Chrome()


def get_beatmaps(user_id):
    user_url = f"{base_url}/{user_id}"
    driver.get(user_url)

    # scroll to "Historical" and give time for data to load
    historical = driver.find_element(By.XPATH, "//div[@data-page-id='historical']")
    historical.location_once_scrolled_into_view
    time.sleep(5)

    element_b = driver.find_elements(By.XPATH, "//div[@class='beatmap-playcount']")

    with open("output8.html", "w", encoding="utf-8") as file:
        file.write(element_b[1].get_attribute("innerHTML"))


get_beatmaps("unko")
