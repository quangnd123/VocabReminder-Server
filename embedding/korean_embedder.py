from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
from mecab import MeCab

class KoreanEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        super().__init__(model=model, tokenizer=tokenizer)
        self.mecab = MeCab()
        self.ignore_pos = ["SF", "SP", "SE", "SS", "SO", "SW"] 
        #SF: Punctuation, SP: Space, SE: End punctuation (e.g., .), SS: Opening punctuation (e.g., “), SO: Other symbols, SW: Foreign symbols

    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[dict]:
        word_data_2d = []
        for sentence in sentences:
            word_data_1d = [{"word": word, "pos": pos} for word, pos in self.mecab.pos(sentence)]
            word_data_2d.append(word_data_1d)    
        return word_data_2d