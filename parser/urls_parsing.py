import argparse
import json
from pandas.core.common import flatten
from functools import wraps

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Lock, Value

from parser import MosRuParser, RiaRuParser, PanoramaParser

N_THREADS = 10

def main(mos_ru_pages: str, ria_pages: str, panorama_pages: str):
    mos_ru_parser = MosRuParser()
    ria_parser = RiaRuParser()
    panorama_parser = PanoramaParser()
    with open(mos_ru_pages, "r") as f:
        mos_ru_urls_dict = json.load(f)
    mos_ru_urls = list(flatten(mos_ru_urls_dict.values()))

    with open(ria_pages, "r") as f:
        ria_urls = json.load(f)
    with open(panorama_pages, "r") as f:
        panorama_urls = json.load(f)

    parse_perform = [
        (mos_ru_parser, mos_ru_urls), (ria_parser, ria_urls), (panorama_parser, panorama_urls)
    ]
    for performer in parse_perform:
        with ThreadPool(processes=N_THREADS) as pool:
            res = pool.map(lambda x: parse(x, parser=performer[0]), performer[1])
        pool.join()
        performer[0].save(res)


def func_wrapper(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        return res
    return wrap


@func_wrapper
def parse(url, parser):
    return parser.parse_page(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsers")
    parser.add_argument("--mos_ru_pages", type=str, required=True,
                        help="path to json with mos.ru urls")
    parser.add_argument("--ria_pages", type=str, required=True,
                        help="path to json with ria.ru urls")
    parser.add_argument("--panorama_pages", type=str, required=True,
                        help="path to json with panorama urls")

    args = parser.parse_args()
    main(mos_ru_pages=args.mos_ru_pages, ria_pages=args.ria_pages, panorama_pages=args.panorama_pages)
