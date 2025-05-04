from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
from pyvi import ViTokenizer, ViPosTagger

class VietnameseEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        super().__init__(model=model, tokenizer=tokenizer)
        self.ignore_pos = {"CH", # symbol
                           "F"} # punctuation
    
    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[dict]:
        word_data_2d = []
        for sentence in sentences:
            tokens, pos_tags = ViPosTagger.postagging(ViTokenizer.tokenize(sentence))
            word_data_1d = [{"word": word.replace("_", " "), "pos": pos} for word, pos in zip(tokens, pos_tags)]
            word_data_2d.append(word_data_1d) 
        return word_data_2d
