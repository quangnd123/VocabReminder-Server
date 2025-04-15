from typing import List
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
    def tokenize_into_words(self, text: str) -> List[str]:
        """
        Split a text into a list of words.

        Args:
            text (str): The input text.

        Returns:
            List[str]: A list of words.
        """
        words = self.tok([text])[0]
        pos_1d = self.pos(words)
        words_data = [{"word": word, "pos": pos} for word, pos in zip(words, pos_1d)]
        return words_data
