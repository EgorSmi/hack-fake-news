import pymorphy2
import pandas as pd
import re
import stanza
from tqdm import tqdm


morph = pymorphy2.MorphAnalyzer() # when server starts
morph_lemmatizer = lambda word: morph.parse(word)[0].normal_form


def lemmatize_text(text: str, lemmatizer=morph_lemmatizer) -> str:
    res = []
    for word in text.split():
        res.append(lemmatizer(word))
    return " ".join(res)


def remove_punctuation_from_text(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text)


def prepare_text(text: str, lemmatizer=morph_lemmatizer) -> str:
    text_without_punctuation = remove_punctuation_from_text(text)
    return lemmatize_text(text_without_punctuation, lemmatizer)

def prepare_df_text_col(df: pd.DataFrame,
                        text_col_name: str,
                        lemmatizer=morph_lemmatizer) -> None:
        df[f'lemmatized_{text_col_name}'] = df[text_col_name].\
            apply(lambda text: prepare_text(text, lemmatizer))

def is_sentence_end(text: str, idx: int) -> bool:
    return text[idx] in '.!?…'

def extract_sentence_by_idx(text: str, idx: int) -> str:
    p_left, p_right = idx, idx
    while p_left > 0 and not is_sentence_end(text, p_left - 1):
        p_left -= 1
    while p_right < len(text) and not is_sentence_end(text, p_right):
        p_right += 1
    return text[p_left:p_right]


def extract_entity_sentence(text: int, entity_idx: int) -> str:
    return extract_sentence_by_idx(text, entity_idx).strip()


def find_all_entities(text: str, entity: str) -> int:
    for match in re.finditer(r'(?:^|\W){}(?:$|\W)'.format(re.escape(entity)),
                             text, re.S):
        yield match.start()
