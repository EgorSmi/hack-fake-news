from abc import abstractmethod
import requests

from bs4 import BeautifulSoup
from lxml import html
import lxml

from tqdm import tqdm

import time
import re
import os
import copy
import stanza
import json
import pymorphy2

from time import sleep


class Parser:
    """Web url parsing util."""
    def __init__(self, output_name: str):
        stanza.download('ru')
        self.nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
        self.morph = pymorphy2.MorphAnalyzer()
        self.output_name = output_name

    def stanza_nlp_ru(self, text):
        doc = self.nlp(text)
        return [f'{ent.text}' for sent in doc.sentences for ent in sent.ents]

    def meta_process(self, page, soup):
        TIME_meta = "article:published_time"
        TITLE_meta = "og:title"

        info = {}
        tree = html.fromstring(page.content)
        head = soup.find("head")
        if head:
            meta = tree.xpath("//meta[@property]")
            for i in meta:
                if i.attrib["property"] == TIME_meta:
                    info["time"] = i.attrib["content"]
                elif i.attrib["property"] == TITLE_meta:
                    info["title"] = i.attrib["content"]

        return info

    def save(self, parsed_urls):
        with open(self.output_name, "wt") as f:
            json.dump(parsed_urls, f)

    @abstractmethod
    def parse_page(self, url: str):
        raise ValueError("Implement me!")


class MosRuParser(Parser):
    """
    Mos.ru news parser.
    """
    def __init__(self, output_name: str = "mos_ru_parsed.json"):
        super().__init__(output_name)

    def parse_page(self, url: str):
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            info = {}
            info["url"] = url

            meta = self.meta_process(page, soup)
            for key in meta.keys():
                info[key] = meta[key]

            tags = []
            a_conts = soup.find_all("a", class_="news-article-tags__link")
            for a in a_conts:
                tags.append(a.text)
            info["tags"] = tags

            body = soup.find("head")
            if body:
                text_content = soup.find("div", class_="content-text")
                text_soup = BeautifulSoup(str(text_content), 'html.parser').find_all("p")
                info["text"] = " ".join(list(map(lambda x: x.text, text_soup))).replace('\xa0', ' ')
                links = []
                base_links = []
                for p in text_soup:
                    for link in p.find_all("a"):
                        links.append(link.get("href"))
                        base_links.append("/".join(link.get("href").split("/")[:3]))
                info["links"] = links
                info["base_links"] = list(set(base_links))
                entities = []
                for word in self.stanza_nlp_ru(info["text"]):
                    p = self.morph.parse(word)[0]
                    entities.append(p.normal_form)

                info["entity"] = list(set(entities))
                return info
        except:
            return {}


class RiaRuParser(Parser):
    """
    Ria.ru news parser
    """
    def __init__(self, output_name: str = "ria_ru_parsed.json"):
        super().__init__(output_name)

    def parse_page(self, url: str):
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            info = {}
            info["url"] = url

            meta = self.meta_process(page, soup)
            for key in meta.keys():
                info[key] = meta[key]

            body = soup.find("body")
            if body:
                text_content = soup.find("div", class_="article__body js-mediator-article mia-analytics")
                text_soup = BeautifulSoup(str(text_content), 'html.parser').find_all("div", class_="article__text")
                info["text"] = " ".join(list(map(lambda x: x.text, text_soup))).replace('\xa0', ' ')
                links = []
                base_links = []
                for p in text_soup:
                    for link in p.find_all("a"):
                        links.append(link.get("href"))
                        base_links.append("/".join(link.get("href").split("/")[:3]))
                info["links"] = links
                info["base_links"] = list(set(base_links))

                entities = []
                raw_entities = []
                for word in self.stanza_nlp_ru(info["text"]):
                    raw_entities.append(word)
                    p = self.morph.parse(word)[0]
                    entities.append(p.normal_form)

                info["entity"] = list(set(entities))
                info["raw_entity"] = list(set(raw_entities))

                tags = body.find_all("a", class_="article__tags-item")
                tags_text = [tag.text for tag in tags]
                info["tags"] = tags_text

            return info

        except:
            return {}
