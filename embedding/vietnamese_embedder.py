from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
from underthesea import pos_tag

class VietnameseEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.ignore_pos = {"CH", # symbol
                           "Ny"} # punctuation
    
    @override
    def tokenize_into_words(self, text: str) -> List[dict]:
        """
        Gets the words data for a text.

        Args:
            text (str): The input sentence.

        Returns:
            List[str]: A list of words.
        """
        words_data = pos_tag(text)
        words_data = [{"word": word, "pos": pos} for word, pos in words_data]
        return words_data
