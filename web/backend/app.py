import re
from typing import List

import time

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Fake news API",
    description='Fake news API',
    root_path='/api'
)


class CheckItem(BaseModel):
    title: str
    content: str


class FindItem(BaseModel):
    name: str
    href: str
    pattern: str


class CheckResponse(BaseModel):
    result: int
    items: List[FindItem]


@app.post('/check')
def check(item: CheckItem):
    time.sleep(2)
    result = CheckResponse(result=99, items=[])
    words = item.content.split()
    pattern = []
    for i, w in enumerate(words):
        q = w
        if i < 6 :
            q = f"<h>{q}<h>";
        pattern.append(q)
    pattern = ' '.join(pattern)
    result.items.append(FindItem(name='title1',href='http://ttt.ru',pattern=pattern))
    return result
