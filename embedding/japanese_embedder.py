from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
from fugashi import Tagger

class JapaneseEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.tagger = Tagger('-Owakati')
        self.ignore_pos = ["補助記号"]  # symbols, punctuation

    @override
    def tokenize_into_words(self, text: str) -> List[str]:
        """
        Split a text into a list of words.

        Args:
            text (str): The input text.

        Returns:
            List[str]: A list of words.
        """
        
        return [{"word": word.surface, "pos": word.pos} for word in self.tagger(text)]
