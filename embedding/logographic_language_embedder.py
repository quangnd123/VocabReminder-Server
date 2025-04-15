from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer

class LogographicLanguagesEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        super().__init__(model=model, tokenizer=tokenizer)
        self.ignore_pos = []

    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[dict]:
        word_2d = self.tokenize_into_tokens(sentences=sentences)
        word_data_2d = []
        for word_1d in word_2d:
            word_data_1d = [{"word": word, "pos": ""} for word in word_1d]
            word_data_2d.append(word_data_1d)
        return word_data_2d