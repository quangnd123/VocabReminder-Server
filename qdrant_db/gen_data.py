import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from qdrant_db.qdrant import AsyncQdrant
from embedding import get_embedders
from logger.logger import get_logger
import asyncio

from dummy_data import sample_data, neg_examples

qdrant_db = AsyncQdrant(collection_name="test", embedding_model_dims=1024, path= "./qdrant_db/db", on_disk=True)
asyncio.run(qdrant_db.create_col())

async def add_phrases(user_id:str):
    for data in sample_data:
        for relation, (language, sentence, phrase) in data.items():
            embedder = get_embedders(language)
            phrase_idx = sentence.find(phrase)

            if phrase_idx < 0:
                print(f"Phrase not found in sentence: {phrase} | {sentence}")
                continue

            new_phrase, new_phrase_idx, phrase_embedding, phrase_context = embedder.get_phrase_embedding(
                sentence=sentence, phrase=phrase, phrase_idx=phrase_idx, with_phrase_context=True
            )

            payload = {
                "user_id": user_id,  # or generate UUIDs if needed
                "language": language,
                "phrase": new_phrase,
                "phrase_idx": new_phrase_idx,
                "sentence": sentence,
                "phrase_context": phrase_context,
            }
            if not phrase == new_phrase:
                print(phrase)
                print(new_phrase)
                print(sentence) 

            await qdrant_db.insert(
                vectors=[phrase_embedding.tolist()],
                payloads=[payload]
            )



    for language, sentence, phrase in neg_examples:
        embedder = get_embedders(language)
        phrase_idx = sentence.find(phrase)

        if phrase_idx < 0:
            print(f"Phrase not found in sentence: {phrase} | {sentence}")
            continue

        new_phrase, new_phrase_idx, phrase_embedding, phrase_context = embedder.get_phrase_embedding(
            sentence=sentence, phrase=phrase, phrase_idx=phrase_idx, with_phrase_context=True
        )
        if not phrase == new_phrase:
            print(phrase)
            print(new_phrase)
            print(sentence) 
        payload = {
            "user_id": user_id,  # or generate UUIDs if needed
            "language": language,
            "phrase": new_phrase,
            "phrase_idx": new_phrase_idx,
            "sentence": sentence,
            "phrase_context": phrase_context,
        }

        await qdrant_db.insert(
            vectors=[phrase_embedding.tolist()],
            payloads=[payload]
        )

    print("Done adding phrases.")

# Run
asyncio.run(add_phrases(user_id="81791df8-8dae-4ec0-a9a9-6283fde47afc"))