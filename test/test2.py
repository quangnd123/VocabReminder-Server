
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

from embedding import EnEmbedder
from transformers import AutoModel, AutoTokenizer
from fastapi import FastAPI, HTTPException, Query, Request
from server.qdrant import AsyncQdrant
from pydantic import BaseModel
from typing import List
import uvicorn
import pprint

model_name = "BAAI/bge-m3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
en_embeder = EnEmbedder(model=model, tokenizer=tokenizer)

qdrant_db = AsyncQdrant(collection_name="test", embedding_model_dims=1024, path= "./qdrant_db", on_disk=True)

app = FastAPI()


class SentenceRequest(BaseModel):
    sentences: List[str]

@app.post("/get_similar_words")
async def create_vector_db(request: SentenceRequest):
   sentences = request.sentences
   word_embedding_2d = en_embeder.get_word_embedding_2d(sentences) #[num_sentences, num_words] an element is a torch.tensor
   word_embedding_2d = [[word_embedding.tolist() for word_embedding in sentence] for sentence in word_embedding_2d] #[num_sentences, num_words] an element is a list of float

   word_2d = [en_embeder.tokenize_into_words(sentence) for sentence in sentences]
   related_phrase_data_3d = await qdrant_db.search_3d(query=word_embedding_2d) #[num_sentences, num_words, num_related_words] an element is a ScorePoint
   
   for word_1d, related_phrase_data_2d, sentence in zip(word_2d, related_phrase_data_3d, sentences):
      pprint.pprint(f"------------Sentence: {sentence}")
      for word, related_phrase_data_1d in zip(word_1d, related_phrase_data_2d):
         pprint.pprint(f"----Word: {word}" )
         pprint.pprint(related_phrase_data_1d.score)
         pprint.pprint(related_phrase_data_1d.payload)
   return

# def main():
#    print("Starting FastAPI server")
#    uvicorn.run(app, host="127.0.0.1", port=8000)

# if __name__ == "__main__":
#     main()

sen1 = "I skipped breakfast"
phrase1 = "breakfast"

sen2 = "The flower jar is broken."
phrase2 = "broken"

sen3 = "I break the law"
phrase3 = "break"


sen5 = "You have to act faster"
phrase5 = "faster"

sen6 = "Hundreds of prisoners began a fast in protest about prison conditions."
phrase6 = "fast"

sen7 = "One day a week he fasts for health reasons."
phrase7 = "fasts"

# cossim = en_embeder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=sen1.find(phrase1), sentence_1=sen1, phrase_2=phrase3, phrase_idx_2=sen3.find(phrase3), sentence_2=sen3)
# print(cossim)

# cossim = en_embeder.get_cossim_phrases(phrase_1=phrase1, phrase_idx_1=sen1.find(phrase1), sentence_1=sen1, phrase_2=phrase6, phrase_idx_2=sen6.find(phrase6), sentence_2=sen6)
# print(cossim)

# print("------------")

# cossim = en_embeder.get_cossim_phrases(phrase_1=phrase6, phrase_idx_1=sen6.find(phrase6), sentence_1=sen6, phrase_2=phrase5, phrase_idx_2=sen5.find(phrase5), sentence_2=sen5)
# print(cossim)

# cossim = en_embeder.get_cossim_phrases(phrase_1=phrase6, phrase_idx_1=sen6.find(phrase6), sentence_1=sen6, phrase_2=phrase7, phrase_idx_2=sen7.find(phrase7), sentence_2=sen7)
# print(cossim)
# print("------------")


# cossim = en_embeder.get_cossim_phrases(phrase_1=phrase2, phrase_idx_1=sen2.find(phrase2), sentence_1=sen2, phrase_2=phrase3, phrase_idx_2=sen3.find(phrase3), sentence_2=sen3)
# print(cossim)

sen10 = "The children's laughter made the room feel joyful."
phrase10 = "joyful"

sen11 = "She felt truly happy when she reunited with her childhood friend after years."
phrase11 = "happy"

cossim = en_embeder.get_cossim_phrases(phrase_1=phrase10, phrase_idx_1=sen10.find(phrase10), sentence_1=sen10, phrase_2=phrase11, phrase_idx_2=sen11.find(phrase11), sentence_2=sen11)
print(cossim)