import argparse

from transformers import AutoTokenizer, AutoModel
from index import InvertedIndex
from scorer import SentenceBertScorer
from tf_idf_searcher import TfidfSearch
import dill as pickle
import stanza



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
                        k_top_candidates=5,
                        scoring_type='bm_25',
                        need_correct: bool=False,
                        entity_per_candidate: int=20):
    white_list_candidates = searcher.search(text, scoring_type=scoring_type,
                                            k_top=k_top_candidates, need_correct=need_correct,
                                            entity_per_candidate=entity_per_candidate)

    if not white_list_candidates:
        return 0
    avg_min_score_per_document = \
        scorer.get_avg_min_score_per_document(white_list_candidates)
    return max(avg_min_score_per_document.items(),
               key=lambda pair: pair[1])


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
    scorer = SentenceBertScorer(sentence_bert_model,
                                sentence_bert_tokenizer)

    return searcher, scorer


def main(index_path: str):
    searcher, scorer = setup(index_path)
    text = """В мире Москва занимает третье место, уступая лишь Нью-Йорку и Сан-Франциско.
    Москва признана первой среди европейских городов в рейтинге инноваций, помогающих в формировании устойчивости коронавирусу. Она опередила Лондон и Барселону.
    Среди мировых мегаполисов российская столица занимает третью строчку — после Сан-Франциско и Нью-Йорка. Пятерку замыкают Бостон и Лондон. Рейтинг составило международное исследовательское агентство StartupBlink.
    Добиться высоких показателей Москве помогло почти 160 передовых решений, которые применяются для борьбы с распространением коронавируса.
    Среди них алгоритмы компьютерного зрения на основе искусственного интеллекта. Это методика уже помогла рентгенологам проанализировать более трех миллионов исследований.
    Еще одно инновационное решение — облачная платформа, которая объединяет пациентов, врачей, медицинские организации, страховые компании, фармакологические производства и сайты.
    Способствовали высоким результатам и технологии, которые помогают адаптировать жизнь горожан во время пандемии. Это проекты в сфере умного туризма, электронной коммерции и логистики, а также дистанционной работы и онлайн-образования.
    Эксперты агентства StartupBlink оценивали принятые в Москве меры с точки зрения эпидемиологических показателей и влияния на экономику."""
    result = estimate_news_paper(text, searcher, scorer, k_top_candidates=10, scoring_type='intersection')
    print(result[1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline")
    parser.add_argument("--index-data", type=str, required=True,
                        help="path to files for index")

    args = parser.parse_args()
    main(index_path=args.index_data)
