from typing import List
from typing_extensions import override 
from .base import BaseEmbedder
from transformers import PreTrainedModel, PreTrainedTokenizer
import spacy 
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.util import compile_infix_regex

class EnglishEmbedder(BaseEmbedder):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> None:
        """Initialize the embedder with the pretrained model."""
        super().__init__(model=model, tokenizer=tokenizer)
        self.ignore_pos = {"SYM", #symbol
                           "PUNCT", #punctuation
                           }
        self.en_spacy = spacy.load("en_core_web_sm")
        self.customize_tokenizer(self.en_spacy)

    def customize_tokenizer(self, nlp):
        """ Make a custom tokenizer so that hyphenated words are not split """
        infixes = (
            LIST_ELLIPSES
            + LIST_ICONS
            + [
                r"(?<=[0-9])[+\-\*^](?=[0-9-])",
                r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                    al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
                ),
                r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
                #r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
                r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
            ]
        )

        infix_re = compile_infix_regex(infixes)

        nlp.tokenizer.infix_finditer = infix_re.finditer
        return

    @override
    def tokenize_into_words(self, sentences: list[str]) -> list[dict]:
        sentence_data_1d = list(self.en_spacy.pipe(sentences))
        word_data_2d =[]
        for sentence_data in sentence_data_1d:
            word_data_1d = [{"word": word.text, "pos": word.pos_} for word in sentence_data]
            word_data_2d.append(word_data_1d)
        return word_data_2d