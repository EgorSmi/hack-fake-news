from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

import sentiment
from pipeline import pipeline

app = FastAPI(
    title="Fake news API",
    description='Fake news API',
    root_path='/api'
)


class CheckItem(BaseModel):
    title: str
    content: str


class SentimentResponse(BaseModel):
    skip: float = 0
    neutral: float = 0
    negative: float = 0
    positive: float = 0


class FindItem(BaseModel):
    name: str
    href: str
    pattern: str
    rating: int
    ner: List[str]
    score: int
    sentiment:Optional[SentimentResponse]


class CheckResponse(BaseModel):
    result: int
    items: List[FindItem]
    sentiment: Optional[SentimentResponse]
    ner: List[str]


@app.on_event('startup')
def startup():
    pipeline.setup('index.pickle')


@app.post('/check')
def check(item: CheckItem):
    score, doc_id_top, doc_sentences = pipeline.estimate_news_paper(item.content)
    #print(candidates)
    #print(scores)
    highlight_info = pipeline.highlight(doc_id_top, doc_sentences)
    result = CheckResponse(result=int(score[1] * 100), items=[], ner=[])
    #items = sorted(zip(candidates, scores.items()), key=lambda x: x[1][1],reverse=True)

    ners = set()
    for id,_ in doc_id_top:
        doc = highlight_info[id]
        for ner in doc['ners']:
            ners.add(ner)
        pattern = item.content

        for sent in doc['sentences']:
            pattern = pattern.replace(sent, f"<h>{sent}<h>")

        find_item = FindItem(name=doc['url'], href=doc['url'], pattern=pattern, rating=50, ner=doc['ners'],
                             score=int(doc['score'] * 100),sentiment=SentimentResponse(**doc['tonality']))
        result.items.append(find_item)
    result.ner = list(ners)
    result.sentiment = SentimentResponse(**sentiment.predict(item.content))

    return result
