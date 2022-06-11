from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import fire
from time import sleep
from abc import abstractmethod


class PagesCrawler:
    """
    Class for urls crawling.
    """
    def __init__(self, web_resource_name: str, output_name: str):
        self.web_resource_name = web_resource_name
        self.output_name = output_name

    @property
    def web_resource(self):
        return self.web_resource_name

    def setup(self):
        pass

    @abstractmethod
    def page_process(self, url):
        raise ValueError("Implement me!")

    def urls_crawling(self, urls):
        self.setup()
        hrefs = {}
        for url in urls:
            try:
                d = self.page_process(url)
            except:
                d = {}
            for key in d:
                if key not in hrefs:
                    hrefs[key] = []
                for value in d[key]:
                    hrefs[key].append(value)

        return hrefs

    def save(self, data):
        with open(self.output_name, "wt") as f:
            json.dump(data, f)


class MosRuCrawler(PagesCrawler):
    """
    Mos.ru crawling util
    """
    def __init__(
            self, web_resource_name: str = "https://www.mos.ru", output_name: str = "mos_ru_pages.json",
            urls_count: int = 68_500, urls_per_page: int = 10
    ):
        super().__init__(web_resource_name, output_name)
        self.urls_count = urls_count
        self.urls_per_page = urls_per_page
        self.pages = self.urls_count // self.urls_per_page

    def setup(self):
        self.executor_path = "./crawler/geckodriver/geckodriver"
        self.driver = webdriver.Firefox(executable_path=self.executor_path)
        self.wait = WebDriverWait(self.driver, 60)

    def page_process(self, url):
        hrefs = {}
        self.driver.get(url)
        reg = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='sc-bwzfXH cZMssy']")))
        urls = self.driver.find_elements(By.XPATH, "//*[@class='sc-VigVT bMaCOi']")
        themes = self.driver.find_elements(By.XPATH,
                                      "//*[@class='Breadcrumbs-result__Item ListItem Breadcrumbs-result__Item--last']")
        if len(urls) != len(themes):
            raise ValueError("Parse Error!")
        for i in range(len(urls)):
            url = urls[i].get_attribute("href")
            theme = themes[i].text
            if theme not in hrefs.keys():
                hrefs[theme] = []
            hrefs[theme].append(url)
        return hrefs

    def urls_crawling(self, urls = []):
        hrefs = {}
        for i in range(1, self.pages + 1):
            url = f"https://www.mos.ru/search?category=newsfeed&page={i}&q="
            try:
                d = self.page_process(url)
            except:
                d = {}
            for key in d:
                if key not in hrefs:
                    hrefs[key] = []
                for value in d[key]:
                    hrefs[key].append(value)

        return hrefs


class RiaNovostiCrawler(PagesCrawler):
    """
    Ria.ru crawling util. Crawling news from ria novosti
    """
    def __init__(self, web_resource_name: str = "https://ria.ru/", output_name: str = "ria_ru_pages.json"):
        super().__init__(web_resource_name, output_name)

    def setup(self):
        self.executor_path = "./crawler/geckodriver/geckodriver"
        self.driver = webdriver.Firefox(executable_path=self.executor_path)
        self.wait = WebDriverWait(self.driver, 60)
        self.spheres = (
            "space", "sn_health", "economy", "society", "incidents",
            "defense_safety", "science", "culture", "religion",
        )
        self.scroll_count = 100

    def page_process(self, url):
        self.driver.get(url)
        hrefs = set()
        current_news_list = set()
        for i in range(self.scroll_count):
            reg = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@class='list-item__title color-font-hover-only']")))
            all_news_list = self.driver.find_elements(By.XPATH, "//*[@class='list-item__title color-font-hover-only']")
            all_news_list = set(all_news_list)
            news_list = all_news_list ^ current_news_list
            current_news_list = all_news_list
            for news in news_list:
                href = news.get_attribute("href")
                if href.startswith("https://ria.ru/"):
                    hrefs.add(href)
            try:
                #  scroll
                next_page = self.driver.find_element(By.XPATH, "//*[@class='list-more']")
                next_page.click()
            except:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(0.5)
        return hrefs

    def urls_crawling(self, urls=[]):
        hrefs_dict = {}
        for sphere in self.spheres:
            sphere_url = self.web_resource + sphere + "/"
            hrefs = self.page_process(sphere_url)
            hrefs_dict[sphere] = list(hrefs)

        return hrefs_list
