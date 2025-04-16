from transformers import AutoModel, AutoTokenizer
from .base import BaseEmbedder
from .logographic_language_embedder import LogographicLanguagesEmbedder
from .space_delimited_language_embedder import SpaceDelimitedLanguagesEmbedder
from .english_embedder import EnglishEmbedder
from .vietnamese_embedder import VietnameseEmbedder
from .chinese_embedder import ChineseEmbedder
from .japanese_embedder import JapaneseEmbedder
from .korean_embedder import KoreanEmbedder


model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

locographic_embedder = LogographicLanguagesEmbedder(model=model, tokenizer=tokenizer)
space_delimited_lang_embedder = SpaceDelimitedLanguagesEmbedder(model=model, tokenizer=tokenizer)
en_embedder = EnglishEmbedder(model=model, tokenizer=tokenizer)
vi_embedder = VietnameseEmbedder(model=model, tokenizer=tokenizer)
zh_embedder = ChineseEmbedder(model=model, tokenizer=tokenizer)
ja_embedder = JapaneseEmbedder(model=model, tokenizer=tokenizer)
ko_embedder = KoreanEmbedder(model=model, tokenizer=tokenizer)

locographic_languages = ["km", "lo", "th", "my"]

supported_embedders: dict[str, BaseEmbedder] = {
    "en": en_embedder,
    "vi": vi_embedder,
    "zh": zh_embedder,
    "yue": zh_embedder,
    "wuu": zh_embedder,
    "ja": ja_embedder,
    "ko": ko_embedder,

    "locographic": locographic_embedder,
    "space-delimited": space_delimited_lang_embedder
}

def get_embedders(language: str) -> BaseEmbedder:
    if language in supported_embedders:
        return supported_embedders[language]
    if language in locographic_languages:
        return supported_embedders["locographic"]
    return supported_embedders["space-delimited"]