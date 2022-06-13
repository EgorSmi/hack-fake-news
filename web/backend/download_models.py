import stanza
from transformers import AutoTokenizer, AutoModel

stanza.download('ru')
nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
sentence_bert_tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
sentence_bert_model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased-sentence")