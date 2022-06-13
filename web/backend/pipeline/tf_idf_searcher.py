from collections import Counter, defaultdict
from typing import List, Optional
import numpy as np

from pipeline.index import InvertedIndex
from pipeline.search_utils import lemmatize_text, find_all_entities, extract_entity_sentence


class TfidfSearch:
    """
    A class for searching for the most relevant tf-idf documents
    """

    def __init__(self, index: InvertedIndex,
                 ner_algorithm,
                 lemmatizer=lemmatize_text):
        self.index = index
        self.ner_algorithm = ner_algorithm
        self.lemmatizer = lemmatizer

    """ document_frequency id is required """
    def is_ready(self):
        return hasattr(self.index, 'document_frequency')

    def calculate_bm25_score(self, document_entity_tf, entity_idf,
                             doc_len, avg_len, b=0.75, k=1.5):
        return entity_idf * (document_entity_tf * (k + 1)) / \
               (document_entity_tf + k * (1 - b + b * (doc_len) / avg_len))

    def calculate_document_rank(self, news_entity_frequency: Counter,
                                document_entity_frequency: Counter,
                                doc_len: int) -> float:
        news_total_entity_frequency = sum(news_entity_frequency.values())
        document_total_frequency = sum(document_entity_frequency.values())
        score = 0
        entity_score = dict()
        for entity in news_entity_frequency:
            if entity not in self.index.index or \
                    entity not in document_entity_frequency:
                continue
            document_entity_tf = document_entity_frequency[entity] / \
                                 document_total_frequency
            entity_idf = np.log((len(self.index.db) - self.index.document_frequency[entity]) /
                                self.index.document_frequency[entity])
            bm_25 = self.calculate_bm25_score(document_entity_tf,
                                              entity_idf,
                                              doc_len,
                                              self.index.avg_document_len)
            score_per_entity = bm_25 * news_total_entity_frequency
            entity_score[entity] = score_per_entity
            score += score_per_entity
        return score, entity_score

    def calculate_intersection_rank(self, news_entites, document_entities):
        entity_intersection = set.intersection(news_entites, document_entities)
        score = 0
        entity_score = dict()
        for entity in entity_intersection:
            if entity not in self.index.index:
                continue
            entity_idf = np.log((len(self.index.db) - self.index.document_frequency[entity]) /
                                  self.index.document_frequency[entity])
            score_per_entity = entity_idf
            entity_score[entity] = score_per_entity
            score += entity_idf
        return score, entity_score

    def get_document_ranking_by_paper(self, paper_text: str,
                                      scoring_type: str='intersection',
                                      pre_candidates: Optional[dict]=None) -> list:
        raw_news_entities = self.ner_algorithm(paper_text)
        paper_entity_context = defaultdict(set)
        news_entity_frequency = defaultdict(int)
        for raw_entity in raw_news_entities:
            normalized_entity = self.lemmatizer(raw_entity)
            for entity_idx in find_all_entities(paper_text, raw_entity):
                entity_context = extract_entity_sentence(paper_text,
                                                          entity_idx)
                paper_entity_context[normalized_entity].add(entity_context)
                news_entity_frequency[normalized_entity] += 1
        unique_news_entities = set(paper_entity_context.keys())
        news_entity_frequency = Counter(news_entity_frequency)
        index_response = self.index.lookup_query(unique_news_entities)
        index_candidates = {appearance.docId
                            for entity_response in index_response.values()
                            for appearance in entity_response
                            if (pre_candidates is None or
                                appearance.docId in pre_candidates)}
        if scoring_type == 'bm_25':
            index_candidates_rank =\
                [(doc_id,
                  *self.calculate_document_rank(
                    news_entity_frequency,
                    self.index.db.get(doc_id)['entity_frequency'],
                    self.index.db.get(doc_id)['text_len']
                  )) for doc_id in index_candidates]
        elif scoring_type == 'intersection':
            index_candidates_rank = [
                (doc_id, *self.calculate_intersection_rank(unique_news_entities,
                                                           set(self.index.db.
                                                               get(doc_id)['entity'])))
                for doc_id in index_candidates
            ]
        return index_candidates_rank, paper_entity_context

    def prepare_candidates(self, candidates: List[List[dict]],
                           paper_entity_context: dict) -> List[dict]:
        formated_candidates = []
        for candidate in candidates:
            candidate_info = {}
            for entity in candidate[2]:
                entity_info = {}
                entity_info['score'] = candidate[2][entity]
                entity_info['src_sentences'] = list(self.index.db.\
                    get(candidate[0])['entity_context'][entity])
                entity_info['query_sentences'] =\
                    list(paper_entity_context[entity])
                if 'entity' not in candidate_info:
                    candidate_info['entity'] = {}
                candidate_info['entity'][entity] = entity_info
            candidate_info['score'] = candidate[1]
            candidate_info['doc_id'] = candidate[0]
            formated_candidates.append(candidate_info)
        return formated_candidates

    def search(self, paper_text: str,
               scoring_type: str='intersection',
               k_top: int=10,
               pre_candidates: Optional[dict]=None):
        document_ranking_by_paper, paper_entity_context =\
            self.get_document_ranking_by_paper(paper_text,
                                               scoring_type,
                                               pre_candidates)
        document_ranking_by_paper_top =\
            sorted(document_ranking_by_paper, key=lambda pair: pair[1] * -1)[:k_top]
        return self.prepare_candidates(document_ranking_by_paper_top,
                                       paper_entity_context)
