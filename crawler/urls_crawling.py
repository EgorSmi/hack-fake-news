import fire

from crawler import MosRuCrawler, RiaNovostiCrawler


def main():
    mos_ru_crawler = MosRuCrawler()
    ria_novosti_crawler = RiaNovostiCrawler()
    crawlers = (mos_ru_crawler, ria_novosti_crawler)
    for crawl in crawlers:
        crawl.setup()
        pages = crawl.urls_crawling()
        crawl.save(pages)


if __name__ == "__main__":
    fire.Fire(main)
