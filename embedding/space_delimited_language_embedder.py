from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
import spacy 

class SpaceDelimitedLanguagesEmbedder(BaseEmbedder):
    """Sentence embedder for all space-delimited languages using a Transformer model."""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.multilingual_spacy = spacy.load("xx_ent_wiki_sm")
        self.ignore_pos = {"SYM", "PUNCT",}

    @override
    def tokenize_into_words(self, text: str) -> List[dict]:
        """
        Gets the words data for a text.

        Args:
            text (str): The input text.

        Returns:
            List[dict]: A list of words data.
        """
        words = self.multilingual_spacy(text)
        words_data = [{"word": word.text, "pos": word.pos_ } for word in words]
        return words_data
