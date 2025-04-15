
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from embedding import get_embedders

eng_embedder = get_embedders("eng")

phrase1 = "tree"
sentence1 = "The tree swayed gently in the wind."
phrase1_idx = sentence1.find(phrase1)

phrase2 = "leaf"
sentence2 = 'A single leaf drifted to the ground.'
phrase2_idx = sentence2.find(phrase2)

phrase3 = "tree"
sentence3 = 'tree'
phrase3_idx = sentence3.find(phrase3)

print(eng_embedder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=phrase1_idx, sentence_1=sentence1, phrase_2=phrase2, phrase_idx_2=phrase2_idx, sentence_2=sentence2))

print(eng_embedder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=phrase1_idx, sentence_1=sentence1, phrase_2=phrase3, phrase_idx_2=phrase3_idx, sentence_2=sentence3))

print(eng_embedder.get_cossim_phrases(phrase_1=phrase2, phrase_idx_1=phrase2_idx, sentence_1=sentence2, phrase_2=phrase3, phrase_idx_2=phrase3_idx, sentence_2=sentence3))