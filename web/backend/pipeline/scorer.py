import numpy as np

import torch
from torch.nn import CosineSimilarity
from typing import List, Optional
from collections import Counter, defaultdict


def get_linalg_norm(input_tensor: torch.Tensor,
                    repeated_shape: int) -> torch.Tensor:
    return torch.linalg.norm(input_tensor, dim=1).repeat(repeated_shape, 1)


def get_cosine_cdist(x1: torch.Tensor, x2: torch.Tensor):
    x1_norm = get_linalg_norm(x1, x2.shape[0]).T
    x2_norm = get_linalg_norm(x2, x1.shape[0])
    return x1 @ x2.T / (x1_norm * x2_norm)


class SentenceBertScorer:
    def __init__(self, sentence_bert_model,
                 sentence_tokenizer,
                 metric: str = 'cosine',
                 p: int = 2):
        self.sentence_bert_model = sentence_bert_model
        self.sentence_tokenizer = sentence_tokenizer
        self.metric = metric
        self.p = p

    def get_score_matrix(self, query_sentences: List[str],
                         src_sentences: List[str]):
        query_tokens = self.sentence_tokenizer(query_sentences,
                                               return_tensors="pt", padding=True)
        src_tokens = self.sentence_tokenizer(src_sentences,
                                             return_tensors="pt", padding=True)
        with torch.no_grad():
            query_emb = \
                self.sentence_bert_model(**query_tokens)['pooler_output']
            src_emb = \
                self.sentence_bert_model(**src_tokens)['pooler_output']

        if self.metric == 'cosine':
            return get_cosine_cdist(query_emb, src_emb)
        elif self.metric == 'minkowski':
            return torch.cdist(query_emb, src_emb, p=2.0)

    def get_k_nearest_neighbours_per_entity(self, query_sentences: List[str],
                                            src_sentences: List[str],
                                            k: int = 1) -> dict:
        score_matrix = self.get_score_matrix(query_sentences,
                                             src_sentences)
        best_k_candidates = \
            score_matrix.topk(k=k, largest=self.metric == 'cosine')
        score_matrix = score_matrix.tolist()
        best_indices = best_k_candidates.indices.tolist()
        query_sentences_pairs = defaultdict(dict)
        for guery_idx in range(len(query_sentences)):
            for top_position, src_idx in enumerate(best_indices[guery_idx]):
                query_sentences_pairs[query_sentences[guery_idx]] \
                    [f'best_{top_position}'] = {
                    'src_sentence': src_sentences[src_idx],
                    'score': score_matrix[guery_idx][src_idx]
                }
        return dict(query_sentences_pairs)

    def get_score_pairs_per_entity(self, query_sentences: List[str],
                                   src_sentences: List[str]) -> dict:
        score_matrix = 1 - self.get_score_matrix(query_sentences,
                                                 src_sentences)
        return score_matrix.max().item()


    def get_score_pairs(self, candidates):
        query_sentences_pairs = defaultdict(dict)
        for candidate in candidates:
            for entity in candidate['entity']:
                src_sentences = candidate['entity'][entity]['src_sentences']
                query_sentences = candidate['entity'][entity]['query_sentences']
                query_sentences_pairs[candidate['doc_id']][entity] = \
                    self.get_score_per_entity(query_sentences, src_sentences)
        return query_sentences_pairs

    def get_avg_min_score_per_document(self, candidates):
        candidate_scores_dict = {}
        for candidate in candidates:
            candidate_score = 0
            accumulate_entity_score = 0
            for entity in candidate['entity']:
                src_sentences = candidate['entity'][entity]['src_sentences']
                query_sentences = candidate['entity'][entity]['query_sentences']
                min_pair_score = self.get_score_pairs_per_entity(query_sentences,
                                                                 src_sentences)
                entity_score = candidate['entity'][entity]['score']
                candidate_score += min_pair_score * entity_score
                accumulate_entity_score += entity_score
            candidate_score = candidate_score / accumulate_entity_score
            candidate_scores_dict[candidate['doc_id']] = candidate_score
        return candidate_scores_dict

    def get_global_score_per_candidate(self, candidate):
        src_sentences = ' '.join(set(sentence for entity in candidate['entity']
                                     for sentence in
                                     candidate['entity'][entity]['src_sentences']))
        query_sentences = ' '.join(set(sentence for entity in candidate['entity']
                                       for sentence in
                                       candidate['entity'][entity]['query_sentences']))

        query_tokens = self.sentence_tokenizer(query_sentences,
                                               return_tensors="pt")
        src_tokens = self.sentence_tokenizer(src_sentences,
                                             return_tensors="pt")
        query_emb = self.sentence_bert_model(**query_tokens)['pooler_output']
        src_emb = self.sentence_bert_model(**src_tokens)['pooler_output']
        cos = CosineSimilarity(dim=1)
        return cos(query_emb, src_emb)