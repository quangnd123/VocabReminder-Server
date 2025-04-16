
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from embedding import get_embedders
import torch.nn.functional as F


def get_cossim_sentences( emb_1, emb_2):
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))

en_embedder = get_embedders("en")
vi_embedder = get_embedders("vi")

phrase1 = "tree"
sentence1 = "The tree swayed gently in the wind."
phrase1_idx = sentence1.find(phrase1)
phrase, phraseidx, emb_1 = en_embedder.get_phrase_embedding(phrase=phrase1, phrase_idx=phrase1_idx, sentence=sentence1)
print(f"{phrase} and {phraseidx}")



# print("VI")
# phrase2 = "cây"
# sentence2 = 'Cái cây rung rinh trong gió.'
# phrase2_idx = sentence2.find(phrase2)
# phrase, phraseidx, emb_2 = vi_embedder.get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
# print(f"{phrase} and {phraseidx}")
# print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))


# print("ZH")
# phrase2 = "树"
# sentence2 = "那棵树在风中轻轻摇曳。"
# phrase2_idx = sentence2.find(phrase2)
# phrase, phraseidx, emb_2 = get_embedders("zh").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
# print(f"{phrase} and {phraseidx}")
# print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))


# print("JA")
# phrase2 = "木"
# sentence2 = "風に揺れる木がありました。"
# phrase2_idx = sentence2.find(phrase2)
# phrase, phraseidx, emb_2 = get_embedders("ja").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
# print(f"{phrase} and {phraseidx}")
# print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))


print("KO")
phrase2 = "나무"
sentence2 = "바람에 나무가 살랑살랑 흔들렸다."
phrase2_idx = sentence2.find(phrase2)
phrase, phraseidx, emb_2 = get_embedders("ko").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
print(f"{phrase} and {phraseidx}")
print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))

print("space")
phrase, phraseidx, emb_2 = get_embedders("space-delimited").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
print(f"{phrase} and {phraseidx}")
print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))

print("loco")
phrase, phraseidx, emb_2 = get_embedders("locographic").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
print(f"{phrase} and {phraseidx}")
print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))





# print(eng_embedder.get_cossim_phrases(phrase_1=phrase1, 
#                                           phrase_idx_1=sentence1.find(phrase1), 
#                                           sentence_1=sentence1, 
#                                           phrase_2=phrase2, 
#                                           phrase_idx_2=phrase2_idx, 
#                                           sentence_2=sentence2))

# words = sentence1.split()
# for word in words:
#     print(word)
#     print(eng_embedder.get_cossim_phrases(phrase_1=word, 
#                                           phrase_idx_1=sentence1.find(word), 
#                                           sentence_1=sentence1, 
#                                           phrase_2=phrase2, 
#                                           phrase_idx_2=phrase2_idx, 
#                                           sentence_2=sentence2))
# words = sentence2.split()
# for word in words:
#     print(word)
#     print(eng_embedder.get_cossim_phrases(phrase_1=word, 
#                                           phrase_idx_1=sentence2.find(word), 
#                                           sentence_1=sentence2, 
#                                           phrase_2=phrase1, 
#                                           phrase_idx_2=phrase1_idx, 
#                                           sentence_2=sentence1))



