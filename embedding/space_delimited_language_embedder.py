from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
import spacy 

class SpaceDelimitedLanguagesEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        super().__init__(model=model, tokenizer=tokenizer)
        self.multilingual_spacy = spacy.load("xx_sent_ud_sm")
        self.ignore_pos = {"SYM", "PUNCT",}

    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[dict]:
        sentence_data_1d = list(self.multilingual_spacy.pipe(sentences))
        word_data_2d =[]
        for sentence_data in sentence_data_1d:
            word_data_1d = [{"word": word.text, "pos": word.pos_} for word in sentence_data]
            word_data_2d.append(word_data_1d)
        return word_data_2d
