from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
from fugashi import Tagger

class JapaneseEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        super().__init__(model=model, tokenizer=tokenizer)
        self.tagger = Tagger('-Owakati')
        self.ignore_pos = ["補助記号"]  # symbols, punctuation

    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[dict]:
        word_data_2d = []
        for sentence in sentences:
            word_data_1d = [{"word": word.surface, "pos": word.pos} for word in self.tagger(sentence)]
            word_data_2d.append(word_data_1d)    
        return word_data_2d
