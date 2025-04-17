
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from embedding import get_embedders
import torch.nn.functional as F


def get_cossim_sentences( emb_1, emb_2):
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))

en_embedder = get_embedders("en")
vi_embedder = get_embedders("vi")

phrase1 = "enjoy"
sentence1 = "She enjoys reading books at night."
phrase1_idx = sentence1.find(phrase1)
phrase, phraseidx, emb_1 = en_embedder.get_phrase_embedding(phrase=phrase1, phrase_idx=phrase1_idx, sentence=sentence1)
print(f"{phrase} and {phraseidx}")

phrase2 = "thích"
sentence2 = "Tôi thích nghe nhạc mỗi khi rảnh."
phrase2_idx = sentence2.find(phrase2)
phrase, phraseidx, emb_2 = get_embedders("vi").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
print(f"{phrase} and {phraseidx}")

print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))
# print("KO")
# phrase2 = "나무"
# sentence2 = "바람에 나무가 살랑살랑 흔들렸다."
# phrase2_idx = sentence2.find(phrase2)
# phrase, phraseidx, emb_2 = get_embedders("ko").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
# print(f"{phrase} and {phraseidx}")
# print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))

# print("space")
# phrase, phraseidx, emb_2 = get_embedders("space-delimited").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
# print(f"{phrase} and {phraseidx}")
# print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))

# print("loco")
# phrase, phraseidx, emb_2 = get_embedders("locographic").get_phrase_embedding(phrase=phrase2, phrase_idx=phrase2_idx, sentence=sentence2)
# print(f"{phrase} and {phraseidx}")
# print(get_cossim_sentences(emb_1=emb_1, emb_2=emb_2))
