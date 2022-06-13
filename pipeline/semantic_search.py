from index import InvertedIndex
from sentence_transformers import util


class SemanticSearch:
    def __init__(self, sentence_transformer_model,
                 index: InvertedIndex):
        self.sentence_transformer_model = sentence_transformer_model
        doc_ids, corpus_embeddings = index.get_corpus_embeddings()
        self.doc_ids = doc_ids
        self.corpus_embeddings = corpus_embeddings

    def search(self, paper_text, k_top: int=10):
        paper_embeddings =\
            self.sentence_transformer_model.encode(paper_text,
                                                   convert_to_tensor=True)
        best_candidates = util.semantic_search(paper_embeddings,
                                               self.corpus_embeddings,
                                               top_k=k_top)[0]
        return {self.doc_ids[candidate['corpus_id']]: candidate['score']
                for candidate in best_candidates}
