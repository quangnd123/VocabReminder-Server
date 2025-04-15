from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
from mecab import MeCab

class KoreanEmbedder(BaseEmbedder):
    """English sentence embedder using a Transformer model."""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.tagger = MeCab()
        self.ignore_pos = ["SF", "SP", "SE", "SS", "SO", "SW"] 
        #SF: Punctuation, SP: Space, SE: End punctuation (e.g., .), SS: Opening punctuation (e.g., “), SO: Other symbols, SW: Foreign symbols

    @override
    def tokenize_into_words(self, text: str) -> List[str]:
        """
        Split a text into a list of words.

        Args:
            text (str): The input text.

        Returns:
            List[str]: A list of words.
        """
        words_data = self.tagger.pos(text)
        return [{"word": word, "pos": pos} for word, pos in words_data]
