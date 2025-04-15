
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")


from embedding import LogographicLangEmbedder, SpaceDelimitedLangEmbedder

from transformers import AutoModel, AutoTokenizer
import time 


start = time.time()
model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

logographic_lang_embedder = LogographicLangEmbedder(model=model, tokenizer=tokenizer)
space_delimited_lang_embedder = SpaceDelimitedLangEmbedder(model=model, tokenizer=tokenizer)
print("Load en_embedder" ,time.time()-start)

sentence = "Mir gönd i de Berg, um de schöne Aussicht z’gnüsse."


print(space_delimited_lang_embedder.tokenize_into_words(text=sentence))
print(space_delimited_lang_embedder.tokenize_into_tokens(text=sentence))
print("----------------------------------")

# print(vi_embeder.get_word_data_1d(sentence_vi))
# print(vi_embeder.tokenize_into_tokens(sentence_vi))
# print("----------------------------------")

# print(logographic_lang_embedder.get_word_data_1d(sentence_logographic))
# print(logographic_lang_embedder.tokenize_into_tokens(sentence_logographic))
# print("----------------------------------")

# print(space_delimited_lang_embedder.get_word_data_1d(sentence_vi))  
# print(space_delimited_lang_embedder.tokenize_into_tokens(sentence_vi))