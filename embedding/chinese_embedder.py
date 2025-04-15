from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
import hanlp

class ChineseEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
        self.pos = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)
        self.ignore_pos= ["w"] #punctuation

    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[str]:
        word_2d = self.tok(sentences)
        pos_2d = self.pos(word_2d)
        word_data_2d = []
        for word_1d, pos_1d in zip(word_2d, pos_2d):
            word_data_1d = [{"word": word, "pos": pos} for word, pos in zip(word_1d, pos_1d)]
            word_data_2d.append(word_data_1d)
        return word_data_2d
