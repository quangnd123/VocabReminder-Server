import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

import uvicorn
import os 
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from collections import defaultdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from models import *
from backend.qdrant_db.qdrant import AsyncQdrant
from posgres_db.postgresql import PostgreSQLDatabase
from llm.free import FreeLLM
from filter import RelatedPhrasesFilter
from embedding import get_embedders
from logger.logger import get_logger
from fasttext_092.language_detection import detect_language


########################## INIT ##########################
base_dir = os.path.dirname(__file__)
common_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=common_env_path)
env = os.getenv("ENV")
#local/prod env
env_path =""
if env == "local":
    env_path = Path(__file__).parent.parent / ".env.local"
elif env =="production":
    env_path = Path(__file__).parent.parent / ".env.production"
load_dotenv(dotenv_path=env_path)

postgres_db_url = os.getenv("POSTGRES_DATABASE_URL")
postgres_db = PostgreSQLDatabase(db_url=postgres_db_url)

logger = get_logger(__name__, "server.log")

freeLLM = FreeLLM()
relatedPhrasesFilter = RelatedPhrasesFilter()
qdrant_db = AsyncQdrant(collection_name="test", embedding_model_dims=1024, path= f"{os.path.dirname(base_dir)}/qdrant_db/db", on_disk=True)

# FastAPI App
app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"chrome-extension://{os.getenv('BROWSER_EXTENSION_ID')}", os.getenv('CLIENT_URL')],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# Define the rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app.state.limiter = limiter
app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)

########################## BROWSER EXTENSION ########################## 

@app.post("/create_phrase")
@limiter.limit("1/second") 
async def create_phrase(create_phrase_request: CreatePhraseRequest, request: Request):
    try:
        user_id = create_phrase_request.user_id
        language = create_phrase_request.language
        sentence = create_phrase_request.sentence
        phrase = create_phrase_request.phrase
        phrase_idx = create_phrase_request.phrase_idx
        
        if not language:
            language, confidence = detect_language(text=sentence)
            if language in ['frr', 'lrc', 'rue']: # unsupported among 176 languages of fasttext
                return CreatePhraseResponse(status="error", error=f"{language} is not supported.")
            if confidence < 0.25:
                return CreatePhraseResponse(status="error", error=f"The language of the phrase not detected. Please specify it.")

        embedder = get_embedders(language=language)

        if phrase == "" or sentence == "":
            return CreatePhraseResponse(status="error", error="Phrase or sentence are empty.")

        # check if phrase is in the sentence
        idx = sentence.find(phrase)
        
        if idx < 0 or phrase != sentence[idx: idx + len(phrase)]:
            logger.info(idx)
            logger.info(sentence)
            logger.info(phrase)
            return CreatePhraseResponse(status="error", error="Something wrong with the phrase index.")

        # check existing phrase in the db
        existing = await qdrant_db.check_exist(filters={"user_id": user_id, 
                                                        "phrase": phrase,
                                                        "phrase_idx": phrase_idx,
                                                        "sentence": sentence,
                                                        "language": language})
        if len(existing[0]) >= 1:
            return CreatePhraseResponse(status="error", error="Phrase already exists.")
        
        # prepare phrase data, then add to the vector db
        new_phrase, new_phrase_idx, phrase_embedding  = embedder.get_phrase_embedding(sentence=sentence, phrase=phrase, phrase_idx=phrase_idx)

        payload = {
            "user_id": user_id,
            "language": language,
            "phrase": new_phrase,
            "phrase_idx": new_phrase_idx,
            "sentence": sentence,
        }
        ids = await qdrant_db.insert(vectors=[phrase_embedding.tolist()], payloads=[payload]) 
        
        return CreatePhraseResponse(status="success", data=PhraseData(id=ids[0],
                                                                 phrase=phrase,
                                                                 phrase_idx=phrase_idx,
                                                                 sentence=sentence,
                                                                 language=language))
    except Exception as e:
        return CreatePhraseResponse(status="error", error=str(e))

@app.post("/get_phrases")
@limiter.limit("1/second") 
async def get_phrases(get_phrase_request: GetPhrasesRequest, request: Request):
    try:
        hits = await qdrant_db.list(filters={"user_id": get_phrase_request.user_id})
        phrase_data_list = [PhraseData(id=hit.id, 
                                        phrase=hit.payload["phrase"], 
                                        phrase_idx=hit.payload["phrase_idx"], 
                                        sentence=hit.payload["sentence"],
                                        language = hit.payload["language"]) for hit in hits]
        return GetPhrasesResponse(status="success", data=phrase_data_list)
    except Exception as e:
        raise GetPhrasesResponse(status="error", error=str(e))
    
@app.post("/delete_phrases")
@limiter.limit("1/second") 
async def delete_phrases(delete_phrases_request: DeletePhrasesRequest, request: Request):
    try:
        await qdrant_db.delete_1d(id_1d=delete_phrases_request.phrase_ids)
        return DeletePhrasesResponse(status="success")
    except Exception as e:
        return DeletePhrasesResponse(status="error", error=str(e))

@app.post("/reminders-text")
@limiter.limit("1/second") 
async def get_reminders_texts(reminders_text_request: RemindersTextRequest, request: Request):
    try:
        user_id = reminders_text_request.user_id
        reading_languages = reminders_text_request.reading_languages
        reminding_language = reminders_text_request.reminding_language
        learning_languages = reminders_text_request.learning_languages

        # detect and filter sentences languages
        sentences = []
        sentences_language = []
        for sentence in reminders_text_request.sentences:
            sentence_language, confidence = detect_language(sentence)
            if confidence >= 0.25 and sentence_language in reading_languages: 
                sentences.append(sentence)
                sentences_language.append(sentence_language)

        # tokenize 
        # all embedders use the same token embedding regardless of language
        token_2d = get_embedders("eng").tokenize_into_tokens(sentences=sentences, add_special_tokens=True) 
        token_embedding_2d = get_embedders("eng").get_token_embedding(sentences=sentences)

        # group sentences of the same languages
        grouped = defaultdict(lambda: {"sentences": [], "token_2d":[], "token_embedding_2d": []})
        for sentence, token_1d, token_embedding_1d, lang in zip(sentences, token_2d, token_embedding_2d, sentences_language):
            grouped[lang]["sentences"].append(sentence)
            grouped[lang]["token_2d"].append(token_1d)
            grouped[lang]["token_embedding_2d"].append(token_embedding_1d)

        sentences = []
        word_data_2d = []
        word_embedding_2d = []
        for lang in grouped.keys():
            lang_word_data_2d, lang_word_embedding_2d = get_embedders(lang).get_word_embedding(grouped[lang]["sentences"], 
                                                                                               token_2d=grouped[lang]["token_2d"], 
                                                                                               token_embedding_2d=grouped[lang]["token_embedding_2d"])
            sentences.extend(grouped[lang]["sentences"])
            word_data_2d.extend(lang_word_data_2d)
            word_embedding_2d.extend([[embedding.tolist() for embedding in embedding_1d] for embedding_1d in lang_word_embedding_2d])

        # search vector db
        related_phrase_data_3d = await qdrant_db.search_3d(query=word_embedding_2d, 
                                                           filters={"user_id": user_id, 
                                                                    "language": {"in": learning_languages}}) #[num_sentences, num_words, num_related_words] an element is a ScorePoint
        logger.info("RELATED DATA")
        for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, related_phrase_data_3d) :
            logger.info("sentence: " + sentence)
            for related_phrase_data_1d, word_data in zip(related_phrase_data_2d, word_data_1d):
                logger.info("word: " + word_data["word"])
                for related_phrase_data in related_phrase_data_1d:
                    logger.info(str(related_phrase_data.score) + " # " + related_phrase_data.payload["phrase"] + " # " + related_phrase_data.payload["sentence"])

        filtered_related_phrase_data_3d = relatedPhrasesFilter.filter(related_phrase_data_3d=related_phrase_data_3d)
        logger.info("FILTERED RELATED DATA")
        for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, filtered_related_phrase_data_3d) :
            logger.info("sentence: " + sentence)
            for related_phrase_data_1d, word_data in zip(related_phrase_data_2d, word_data_1d):
                logger.info("word: " + word_data["word"])
                for related_phrase_data in related_phrase_data_1d:
                    logger.info(str(related_phrase_data.score) + " # " + related_phrase_data.payload["phrase"] + " # " + related_phrase_data.payload["sentence"])
        
        sentence_data_1d = []
        for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, filtered_related_phrase_data_3d):
            sentence_data_1d.append({"sentence": sentence, "word_data_1d": word_data_1d, "related_phrase_data_2d": related_phrase_data_2d})       

        prompt_tokens_num, completion_tokens_num, response_time = await freeLLM.get_reminders_text(sentence_data_1d=sentence_data_1d, reminding_language = reminding_language, free_llm = reminders_text_request.free_llm)
        
        data = relatedPhrasesFilter.sample_reminder(sentence_data_1d=sentence_data_1d)

        # track user activity
        sentences_num = len(sentences)
        words_num = sum(len(word_data_1d) for word_data_1d in word_data_2d)
        related_words_num = sum(len(related_phrase_data_1d) for related_phrase_data_2d in related_phrase_data_3d for related_phrase_data_1d in related_phrase_data_2d)
        filter_related_words_num = sum(len(related_phrase_data_1d) for related_phrase_data_2d in filtered_related_phrase_data_3d for related_phrase_data_1d in related_phrase_data_2d)
        
        postgres_db.track_user_reminders_text_activity(user_id=user_id, 
                                                       sentences_num=sentences_num,
                                                       words_num = words_num,
                                                       related_words_num=related_words_num,
                                                       filter_related_words_num=filter_related_words_num,
                                                       prompt_tokens_num=prompt_tokens_num,
                                                       completion_tokens_num=completion_tokens_num,
                                                       response_time_ms=response_time
                                                       )

        return RemindersTextResponse(status="success", data=data)
    except Exception as e:
        raise RemindersTextResponse(status="error", error=str(e))

########################## CLient ##########################

@app.post("/update_user")
@limiter.limit("1/second") 
async def update_user(updated_user: UpdateUserRequest, request: Request):
    try:
        user = await postgres_db.update_user(user_id=updated_user.id, 
                                       name=updated_user.name, 
                                       reading_languages=updated_user.reading_languages,
                                       learning_languages=updated_user.learning_languages,
                                       reminding_language=updated_user.reminding_language,
                                       free_llm=updated_user.free_llm,
                                       unallowed_urls=updated_user.unallowed_urls)
        if not user: 
            return UpdateUserResponse(status="error", error="User not found")
        
        return UpdateUserResponse(status="success", data=User(id=user.id, 
                                                              name=user.name, 
                                                              email=user.email, 
                                                              reading_languages=user.reading_languages,
                                                              learning_languages=user.learning_languages,
                                                              reminding_language=user.reminding_language,
                                                              free_llm=user.free_llm,
                                                              unallowed_urls=user.unallowed_urls))
    except Exception as e:
        return UpdateUserResponse(status="error", error=str(e))


@app.get("/get_free_LLMs")
@limiter.limit("1/second") 
async def get_free_LLMs(request: Request):
    try:
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "llm", "free_llm.json")
        with open(json_file_path, 'r') as f:
            free_llm = json.load(f)
        free_llm_ids = [llm["id"] for llm in free_llm]
        return GetFreeLLMsResponse(status="success", data=free_llm_ids)
    except Exception as e:
        return GetFreeLLMsResponse(status="error", error=str(e))
    

def main():
    print("Starting FastAPI server")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()