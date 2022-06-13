from collections import Counter, defaultdict

import argparse
import itertools
import json
import numpy as np
import pandas as pd
import pymorphy2
import torch
from tqdm import tqdm
import re
import dill as pickle
from typing import List, Optional

from pipeline.search_utils import (
    lemmatize_text, find_all_entities, extract_entity_sentence
)

text_lemmatizer = lambda text: lemmatize_text(text)


class Appearance:
    """
    Represents the appearance of a term in a given document, along with the
    frequency of appearances in the same one.
    """

    def __init__(self, docId: int, frequency: int):
        self.docId = docId
        self.frequency = frequency

    def __repr__(self):
        """
        String representation of the Appearance object
        """
        return str(self.__dict__)


class Database:
    """
    In memory database representing the already indexed documents.
    """

    def __init__(self):
        self.db = dict()

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.__dict__)

    def __len__(self):
        return len(self.db)

    def get(self, docId: int) -> Optional[dict]:
        return self.db.get(docId, None)

    def add(self, document: dict) -> None:
        """
        Adds a document to the DB.
        """
        return self.db.update({document['id']: document})

    def remove(self, docId: int):
        """
        Removes document from DB.
        """
        return self.db.pop(docId, None)

    def keys(self):
        return self.db.keys()


class InvertedIndex:
    """
    Inverted Index class.
    """
    def __init__(self, db: Database,
                 entity_lemmatizer=text_lemmatizer,
                 entity_context_len=10):
        self.index = dict()
        self.db = db
        self.entity_lemmatizer = entity_lemmatizer
        self.entity_context_len = entity_context_len

    def __repr__(self):
        """
        String representation of the Database object
        """
        return str(self.index)

    def index_document(self, document: dict, raw_entities_col_name: str) -> dict:
        """
        Process a given document, save it to the DB and update the index.
        entities_alphabet: key is a normalized entity, value - raw entities' set
        """
        appearances_dict = defaultdict(int)
        document['entity_context'] = defaultdict(set)
        # Dictionary with each term and the frequency it appears in the text.
        for raw_entity in document[raw_entities_col_name]:
            normalized_entity = self.entity_lemmatizer(raw_entity)
            for entity_idx in find_all_entities(document['text'], raw_entity):
                entity_frequency = appearances_dict[normalized_entity].frequency if\
                    normalized_entity in appearances_dict else 0
                appearances_dict[normalized_entity] = Appearance(document['id'],
                                                             entity_frequency + 1)
                entity_context = extract_entity_sentence(document['text'],
                                                          entity_idx)
                document['entity_context'][normalized_entity].add(entity_context)
        document['embedding'] =\
            torch.tensor(document['rubert-base-cased-sentence_embedding'])
        document['entity_context'] = dict(document['entity_context'])
        document['text_len'] = len(document['text'].split())
        document['entity_frequency'] =\
            Counter({key: appearance.frequency for
                     key, appearance in appearances_dict.items()})
        # Update the inverted index
        update_dict = { key: [appearance]
                       if key not in self.index
                       else self.index[key] + [appearance]
                       for (key, appearance) in appearances_dict.items() }
        self.index.update(update_dict)
        # Add the document into the database
        self.db.add(document)
        return document

    def lookup_query(self, normalized_entities: set) -> dict:
        """
        Returns the dictionary of terms with their correspondent Appearances.
        This is a very naive search since it will just split the terms and show
        the documents where they appear.
        """
        return { entity: self.index[entity] for entity in normalized_entities
                if entity in self.index }

    def calculate_document_frequency_per_entity(self):
        self.document_frequency = defaultdict(int)
        for entity in self.index:
            self.document_frequency[entity] += len(self.index[entity])

    def calculate_avg_document_len(self):
        self.avg_document_len = 0
        for doc_id in self.db.keys():
            self.avg_document_len += self.db.get(doc_id)['text_len'] / len(self.db)

    def get_corpus_embeddings(self):

        doc_ids = list(self.db.keys())
        return doc_ids, torch.stack([self.db.get(doc_id)['embedding']
                                     for doc_id in doc_ids])


def create_index(document_collection: List[dict],
                 raw_entity_col_name: str='raw_entity') -> InvertedIndex:
    db = Database()
    index = InvertedIndex(db)

    doc_id = 0
    for document in tqdm(document_collection):
        document['id'] = doc_id
        index.index_document(document, raw_entity_col_name)
        doc_id += 1
    index.calculate_document_frequency_per_entity()
    index.calculate_avg_document_len()
    return index


def main(index_path: str):
    with open(index_path, "rt") as f:
        index_data = json.load(f)
    index = create_index(index_data, 'raw_entity')

    with open("index.pickle", "wb") as f:
        pickle.dump(index, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsers")
    parser.add_argument("--index_data", type=str, required=True,
                        help="path to files for index")

    args = parser.parse_args()
    main(index_path=args.index_data)
