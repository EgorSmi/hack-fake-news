import fire

from crawler import MosRuCrawler, RiaNovostiCrawler, PanoramaCrawler


def main():
    mos_ru_crawler = MosRuCrawler()
    ria_novosti_crawler = RiaNovostiCrawler()
    panorama_crawler = PanoramaCrawler()
    crawlers = [mos_ru_crawler, ria_novosti_crawler, panorama_crawler]
    for crawl in crawlers:
        crawl.setup()
        pages = crawl.urls_crawling()
        crawl.save(pages)


if __name__ == "__main__":
    fire.Fire(main)
