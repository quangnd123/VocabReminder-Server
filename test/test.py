
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from embedding import get_embedders
import torch.nn.functional as F
from qdrant_db.dummy_data import original_words, sample_data

def get_cossim_sentences( emb_1, emb_2):
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))

en_embedder = get_embedders("en")
vi_embedder = get_embedders("vi")

phrase1 = "shout"
sentence1 = "He had to shout over the noise to be heard."
idx1 = sentence1.find(phrase1)

phrase2 = "bellowed"
sentence2 = "He bellowed like a furious lion."
idx2 = sentence2.find(phrase2)

print(en_embedder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=idx1, sentence_1=sentence1,
                               phrase_2=phrase2, phrase_idx_2=idx2, sentence_2=sentence2))

phrase1 = "shout"
sentence1 = "shout"
idx1 = sentence1.find(phrase1)

phrase2 = "bellowed"
sentence2 = "He bellowed like a furious lion."
idx2 = sentence2.find(phrase2)

print(en_embedder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=idx1, sentence_1=sentence1,
                               phrase_2=phrase2, phrase_idx_2=idx2, sentence_2=sentence2))

phrase1 = "shout"
sentence1 = "He had to shout over the noise to be heard."
idx1 = sentence1.find(phrase1)

phrase2 = "bellowed"
sentence2 = "bellowed"
idx2 = sentence2.find(phrase2)

print(en_embedder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=idx1, sentence_1=sentence1,
                               phrase_2=phrase2, phrase_idx_2=idx2, sentence_2=sentence2))

phrase1 = "shout"
sentence1 = "shout"
idx1 = sentence1.find(phrase1)

phrase2 = "bellowed"
sentence2 = "bellowed"
idx2 = sentence2.find(phrase2)

print(en_embedder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=idx1, sentence_1=sentence1,
                               phrase_2=phrase2, phrase_idx_2=idx2, sentence_2=sentence2))

# for i in range(5):
#     _, sen, word = original_words[i]
#     phrase_idx = sen.find(word)
#     phrase, phraseidx, emb_1 = get_embedders("en").get_phrase_embedding(phrase=word, phrase_idx=phrase_idx, sentence=sen)
#     print("--------------------------------")
#     print(word + " ---- " + sen)
#     print(phrase)
#     for relation, (language, sentence, phrase) in sample_data[i].items():
#         idx   = sentence.find(phrase)
#         p, phraseidx, emb_2 = get_embedders("en").get_phrase_embedding(phrase=phrase, phrase_idx=idx, sentence=sentence)
#         print(phrase + " ---- " + sentence)
#         print(p)
#         print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))

