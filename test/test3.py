import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from server.qdrant import AsyncQdrant
from embedding import get_embedders
from logger.logger import get_logger
import asyncio

from data import sample_data

qdrant_db = AsyncQdrant(collection_name="test", embedding_model_dims=1024, path= "./qdrant_db", on_disk=True)
asyncio.run(qdrant_db.create_col())

async def add_phrases():
    for language, sentence, phrase in sample_data:
        embedder = get_embedders(language)
        phrase_idx = sentence.find(phrase)

        if phrase_idx < 0:
            print(f"Phrase not found in sentence: {phrase} | {sentence}")
            continue

        new_phrase, new_phrase_idx, phrase_embedding = embedder.get_phrase_embedding(
            sentence=sentence, phrase=phrase, phrase_idx=phrase_idx
        )

        payload = {
            "user_id": "0",  # or generate UUIDs if needed
            "language": language,
            "phrase": new_phrase,
            "phrase_idx": new_phrase_idx,
            "sentence": sentence,
        }

        await qdrant_db.insert(
            vectors=[phrase_embedding.tolist()],
            payloads=[payload]
        )

    print("Done adding phrases.")

# Run
asyncio.run(add_phrases())