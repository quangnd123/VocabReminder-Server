from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer

class LogographicLanguagesEmbedder(BaseEmbedder):
    """Sentence embedder for all logographic languages using a Transformer model."""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.ignore_pos = []

    @override
    def tokenize_into_words(self, text: str) -> List[dict]:
        """
        Gets the words data for a text.

        Args:
            text (str): The input text.

        Returns:
            List[dict]: A list of words data.
        """
        words_data = [{"word": word, "pos": ""} for word in self.tokenize_into_tokens(text)]
        return words_data