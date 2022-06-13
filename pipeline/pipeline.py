import argparse
from typing import Optional, Any

from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from index import InvertedIndex, Database
from scorer import SentenceBertScorer
from tf_idf_searcher import TfidfSearch
from semantic_search import SemanticSearch
import dill as pickle
import stanza
import itertools


def stanza_nlp_ru(text, nlp):
    doc = nlp(text)
    return [f'{ent.text}' for sent in doc.sentences for ent in sent.ents]


def get_raw_entities_from_text(text: str, nlp) -> list:
    raw_entities = []
    for word in stanza_nlp_ru(text, nlp):
        raw_entities.append(word)
    return raw_entities


def estimate_news_paper(text: str,
                        searcher: TfidfSearch,
                        scorer: SentenceBertScorer,
                        semantic_searcher,
                        k_top_candidates=5,
                        scoring_type='bm_25',
                        k_top_precandidates=100,
                        semantic_average: bool = False,
                        highlight_k_top: int = 3):
    pre_candidates = semantic_searcher.search(text, k_top_precandidates)

    white_list_candidates = searcher.search(text, scoring_type=scoring_type,
                                            k_top=k_top_candidates,
                                            pre_candidates=pre_candidates)
    if not white_list_candidates:
        return 0, [], []
    avg_min_score_per_document = \
        scorer.get_avg_min_score_per_document(white_list_candidates)

    white_list_candidates_similarity = {candidate['doc_id']: pre_candidates[candidate['doc_id']]
                                        for candidate in white_list_candidates}
    avg_min_score_per_document_sorted = sorted(white_list_candidates_similarity.items(),
                                               key=lambda pair: pair[1], reverse=True)
    if semantic_average:
        score = 0
        total_semantic_score = 0
        max_doc_id = None
        for doc_id in avg_min_score_per_document:
            semantic_score = pre_candidates[doc_id]
            doc_id_score = avg_min_score_per_document[doc_id] * semantic_score
            score += doc_id_score
            if (max_doc_id is None or
                    avg_min_score_per_document[max_doc_id] < doc_id_score):
                max_doc_id = doc_id
            total_semantic_score += semantic_score
        res = (max_doc_id, 1 - (score / total_semantic_score))
    else:
        res = max(avg_min_score_per_document.items(),
                  key=lambda pair: pair[1])
        doc_id, score = res
        res = (doc_id, 1 - score)

    doc_id_top = []
    for document in avg_min_score_per_document_sorted[:highlight_k_top]:
        doc_id_top.append(document)
    return res, doc_id_top, white_list_candidates


def highlight(doc_id_top: list,
              doc_sentences: dict,
              indexdb: Database):
    info = dict()

    for pair in doc_id_top:
        id_ = pair[0]
        score = pair[1]
        info[id_] = dict()
        info[id_]["url"] = indexdb.get(id_)["url"]
        info[id_]["score"] = score
        info[id_]["tonality"] = indexdb.get(id_)["tonality"]
    for doc_sentence in doc_sentences:
        if doc_sentence["doc_id"] in doc_id_top:
            orig_sentences = list(set(list(itertools.chain(*list(map(lambda x: x["src_sentences"],
                                                                     list(doc_sentence["entity"].values())))))))
            info[doc_sentence["doc_id"]]["sentences"] = orig_sentences
    return info


def setup(index_path: str):
    with open(index_path, "rb") as f:
        index = pickle.load(f)

    print(index.index["собянин"])
    stanza.download('ru')
    nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
    ner_algorithm = lambda text: get_raw_entities_from_text(text, nlp)
    searcher = TfidfSearch(index, ner_algorithm=ner_algorithm)
    sentence_bert_tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
    sentence_bert_model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
    embedder = SentenceTransformer('DeepPavlov/rubert-base-cased-sentence')
    semantic_searcher = SemanticSearch(embedder, index)
    scorer = SentenceBertScorer(sentence_bert_model,
                                sentence_bert_tokenizer)

    return index.db, searcher, scorer, semantic_searcher


def main(index_path: str):
    db, searcher, scorer, semantic_searcher = setup(index_path)
    text = """cобянин приехал в москву"""
    result, doc_id_top, doc_sentences = estimate_news_paper(text, searcher, scorer, k_top_candidates=10, scoring_type='intersection',
                    semantic_searcher=semantic_searcher)
    print(result)
    highlight_info = highlight(doc_id_top, doc_sentences, db)
    print("highlight_info: ", highlight_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline")
    parser.add_argument("--index-data", type=str, required=True,
                        help="path to files for index")

    args = parser.parse_args()
    main(index_path=args.index_data)
