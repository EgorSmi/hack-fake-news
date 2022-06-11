from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import fire


URLS_COUNT = 68_500
URLS_PER_PAGE = 10
PAGES = URLS_COUNT // 10


def page_process(driver, wait, number):
    mos_ru = f"https://www.mos.ru/search?category=newsfeed&page={number}&q="
    hrefs = {}
    driver.get(mos_ru)
    reg = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='sc-bwzfXH cZMssy']")))
    urls = driver.find_elements(By.XPATH, "//*[@class='sc-VigVT bMaCOi']")
    themes = driver.find_elements(By.XPATH, "//*[@class='Breadcrumbs-result__Item ListItem Breadcrumbs-result__Item--last']")
    if len(urls) != len(themes):
        raise ValueError("Parse Error!")
    for i in range(len(urls)):
        url = urls[i].get_attribute("href")
        theme = themes[i].text
        if theme not in hrefs.keys():
            hrefs[theme] = []
        hrefs[theme].append(url)
    return hrefs


def urls_crawling(executable_path="/Users/egor.smirnov/Documents/parser/geckodriver"):
    driver = webdriver.Firefox(executable_path=executable_path)
    wait = WebDriverWait(driver, 3600)
    hrefs = {}
    for i in range(1, PAGES + 1):
        try:
            d = page_process(driver, wait, i)
        except:
            d = {}
        for key in d:
            if key not in hrefs:
                hrefs[key] = []
            for value in d[key]:
                hrefs[key].append(value)

    return hrefs


def main():
    hrefs = urls_crawling()

    with open("page_urls.json", "wt") as f:
        json.dump(hrefs, f)


if __name__ == "__main__":
    fire.Fire(main)
