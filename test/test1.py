
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from embedding import get_embedders
from qdrant_db.qdrant import AsyncQdrant
from logger.logger import get_logger
import asyncio
from qdrant_db.dummy_data import original_words


qdrant_db = AsyncQdrant(collection_name="test", embedding_model_dims=1024, path= "./qdrant_db/db", on_disk=True)

async def f():
    idx = 0
    for (lang, sentence, phrase) in original_words:
        phrase_idx = sentence.find(phrase)
        phrase, phraseidx, emb_1 = get_embedders(lang).get_phrase_embedding(phrase=phrase, phrase_idx=phrase_idx, sentence=sentence)
        related_phrase_data_1d = await qdrant_db.search_1d(query=emb_1.tolist(), filters={"language": "en" }, limit = 20)
        
        logger = get_logger(__name__, "server.log")
        logger.info("RELATED DATA")
        logger.info("sentence: " + sentence)
        logger.info("word: " + phrase)
        for related_phrase_data in related_phrase_data_1d:
            logger.info(str(related_phrase_data.score) + " # " + related_phrase_data.payload["phrase"] + " # " + related_phrase_data.payload["sentence"])

asyncio.run(f())