import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

import uvicorn
import os 
import time
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from collections import defaultdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import asyncio

from model.models import *
from qdrant_db.qdrant import AsyncQdrant
from posgres_db.postgresql import PostgreSQLDatabase
from llm.free import FreeLLM
from filter import RelatedPhrasesFilter
from embedding import get_embedders, embedding_model_dims, max_token_num
from logger.logger import get_logger, get_error_logger
from fasttext_092.language_detection import detect_language


########################## ENV ##########################
base_dir = os.path.dirname(__file__)
common_env_path = Path(__file__).parent.parent / ".env"

load_dotenv(dotenv_path=common_env_path)

env = os.getenv("ENV")
env_path =""
if env == "development":
    env_path = Path(__file__).parent.parent / ".env.development"
elif env =="production":
    env_path = Path(__file__).parent.parent / ".env.production"
load_dotenv(dotenv_path=env_path)


########################## INIT ##########################
logger = get_logger("server", "server.log")
error_logger = get_error_logger("server_errors")

postgres_db_url = os.getenv("POSTGRES_DATABASE_URL")
postgres_db = PostgreSQLDatabase(db_url=postgres_db_url)

qdrant_db_url = os.getenv("QDRANT_HTTP_URL")
qdrant_db = AsyncQdrant(url=qdrant_db_url, collection_name="VocabReminder", embedding_model_dims=embedding_model_dims)

freeLLM = FreeLLM()
relatedPhrasesFilter = RelatedPhrasesFilter()


########################## FASTAPI ##########################
app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"chrome-extension://{os.getenv('BROWSER_EXTENSION_EDGE_ID')}", os.getenv('CLIENT_URL')],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)

# Define the rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app.state.limiter = limiter
app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)


########################## USER ########################## 

@app.post("/update_user")
@limiter.limit("1/second") 
async def update_user(updated_user: UpdateUserRequest, request: Request):
    try:
        user: User = await postgres_db.update_user(user_id=updated_user.id, 
                                       name=updated_user.name, 
                                       reading_languages=updated_user.reading_languages,
                                       learning_languages=updated_user.learning_languages,
                                       llm_response_language=updated_user.llm_response_language,
                                       unallowed_urls=updated_user.unallowed_urls)
        if not user: 
            return UpdateUserResponse(status="error", error="User not found")
        
        return UpdateUserResponse(status="success", data=User(id=user.id, 
                                                              name=user.name, 
                                                              email=user.email, 
                                                              reading_languages=user.reading_languages,
                                                              learning_languages=user.learning_languages,
                                                              llm_response_language=user.llm_response_language,
                                                              unallowed_urls=user.unallowed_urls))
    except Exception as e:
        return UpdateUserResponse(status="error", error=str(e))


########################## PHRASE ########################## 

@app.post("/create_phrase")
@limiter.limit("1/second") 
async def create_phrase(create_phrase_request: CreatePhraseRequest, request: Request):
    try:
        user_id = create_phrase_request.user_id
        language = create_phrase_request.language
        sentence = create_phrase_request.sentence
        phrase = create_phrase_request.phrase
        phrase_idx = create_phrase_request.phrase_idx

        if not phrase:
            return CreatePhraseResponse(status="error", error="Phrase or sentence are empty.")
        
        if not language:
            if sentence:
                language = detect_language(text=sentence)
            else:
                language = detect_language(text=phrase)
            if language in ['frr', 'lrc', 'rue']: # unsupported among 176 languages of fasttext
                return CreatePhraseResponse(status="error", error=f"{language} is not supported.")
            if language == "unknown":
                return CreatePhraseResponse(status="error", error=f"The language of the phrase not detected. Please specify it.")
        
        if not sentence:
            sentence = await freeLLM.create_sentence(phrase=phrase, language=language)
            phrase_idx = sentence.find(phrase)
            if phrase_idx < 0:
                return CreatePhraseResponse(status="error", error="Something wrong with auto sentence creation. Please add the sentence manually.")
        else:
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
        embedder = get_embedders(language=language)
        new_phrase, new_phrase_idx, phrase_embedding, phrase_context  = embedder.get_phrase_embedding(sentence=sentence, phrase=phrase, phrase_idx=phrase_idx, with_phrase_context=True)

        payload = {
            "user_id": user_id,
            "language": language,
            "phrase": new_phrase,
            "phrase_idx": new_phrase_idx,
            "sentence": sentence,
            "phrase_context": phrase_context,
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

@app.post("/translate_phrase")
@limiter.limit("1/second") 
async def translate_phrase(translate_phrase_request: TranslatePhraseRequest, request: Request):
    try:
        translation = await freeLLM.translate_phrase(translate_phrase_request=translate_phrase_request)
        return TranslatePhrasesResponse(status="success", data=translation)
    except Exception as e:
        return TranslatePhrasesResponse(status="error", error=str(e))


########################## REMINDER TEXT ##########################

@app.websocket("/ws/reminders-text")
async def get_reminders_texts( websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_json()
            reminders_text_request = RemindersTextRequest(**msg) 

            # Handle each request in its own coroutine
            asyncio.create_task(generate_reminders_texts(websocket, reminders_text_request))

    except WebSocketDisconnect:
        pass

async def generate_reminders_texts(websocket: WebSocket, reminders_text_request: RemindersTextRequest):
    try:
        start_time = time.time()

        tab_id = reminders_text_request.tab_id
        request_id = reminders_text_request.request_id
        user_id = reminders_text_request.user_id
        reading_languages = reminders_text_request.reading_languages
        llm_response_language = reminders_text_request.llm_response_language
        learning_languages = reminders_text_request.learning_languages

        # Step 1: detect and filter sentences languages
        sentences = []
        sentences_language = []
        for sentence in reminders_text_request.sentences:
            if "\n" in sentence:
                continue
            if len(sentence) + 2 > max_token_num: # 2 for <s> and </s> tokens # not too correct check
                continue
            sentence_language = detect_language(sentence)
            if sentence_language != "unknown" and sentence_language in reading_languages: 
                sentences.append(sentence)
                sentences_language.append(sentence_language)

        if len(sentences) == 0:
            await websocket.send_json(RemindersTextResponse(status="success", data=RemindersTextResponseData(tab_id=tab_id, request_id=request_id, is_final=True, reminders_text_data=[])).model_dump())
            return
        
        # Step 2: tokenize sentences, all embedders use the same token embedding regardless of language
        token_2d = get_embedders("default").tokenize_into_tokens(sentences=sentences, add_special_tokens=True) 
        token_embedding_2d = get_embedders("default").get_token_embedding(sentences=sentences)

        # Step 3: group sentences of the same languages, diff languages have diff word tokenizers
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

        # Step 4: search vector db
        related_phrase_data_3d = await qdrant_db.search_3d(word_embedding_2d=word_embedding_2d, 
                                                           word_data_2d=word_data_2d,
                                                           filters={"user_id": user_id, 
                                                                    "language": {"in": learning_languages}}) #[num_sentences, num_words, num_related_words] an element is a ScorePoint
        # logger.info("RELATED DATA")
        # for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, related_phrase_data_3d) :
        #     logger.info("sentence: " + sentence)
        #     for related_phrase_data_1d, word_data in zip(related_phrase_data_2d, word_data_1d):
        #         if len(related_phrase_data_1d) == 0:
        #             continue
        #         logger.info("word: " + word_data["word"])
        #         for related_phrase_data in related_phrase_data_1d:
        #             logger.info(str(related_phrase_data.score) + " # " + related_phrase_data.payload["phrase"] + " # " + related_phrase_data.payload["sentence"])

        # Step 5: filter related phrases
        filtered_related_phrase_data_3d = relatedPhrasesFilter.filter(related_phrase_data_3d=related_phrase_data_3d)
        # logger.info("FILTERED RELATED DATA")
        # for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, filtered_related_phrase_data_3d) :
        #     if not any(related_phrase_data_1d for related_phrase_data_1d in related_phrase_data_2d):
        #         continue
        #     logger.info("sentence: " + sentence)
        #     for related_phrase_data_1d, word_data in zip(related_phrase_data_2d, word_data_1d):
        #         if len(related_phrase_data_1d) == 0:
        #             continue
        #         logger.info("word: " + word_data["word"])
        #         for related_phrase_data in related_phrase_data_1d:
        #             logger.info(str(related_phrase_data.score) + " # " + related_phrase_data.payload["phrase"] + " # " + related_phrase_data.payload["sentence"])
        
        # Step 6: create sentence data
        sentence_data_1d = []
        for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, filtered_related_phrase_data_3d):
            sentence_data_1d.append({"sentence": sentence, "word_data_1d": word_data_1d, "related_phrase_data_2d": related_phrase_data_2d})       

        # Step 7: get reminders text, add reminder to sentences' data
        response_time=0
        async for response in freeLLM.get_reminders_text(sentence_data_1d=sentence_data_1d, llm_response_language = llm_response_language):
            # record response time
            now_time = time.time()
            if now_time-start_time > response_time:
                response_time = now_time-start_time
            
            logger.info(response)
            if response["reminders_text_data"] or response["end"] == True:
                reminders_text_data=[]
                for reminder_text_data in response["reminders_text_data"]:
                    reminders_text_data.append(ReminderTextData(**reminder_text_data))
                data = RemindersTextResponseData(tab_id=tab_id, request_id=request_id, reminders_text_data=reminders_text_data, is_final=response["end"])
                await websocket.send_json(RemindersTextResponse(status="success", data=data).model_dump())    
            
            if response["end"] == True and response["prompt_tokens"]:
                # track user activity
                sentences_num = len(sentences)
                words_num = sum(len(word_data_1d) for word_data_1d in word_data_2d)
                related_words_num = sum(len(related_phrase_data_1d) for related_phrase_data_2d in related_phrase_data_3d for related_phrase_data_1d in related_phrase_data_2d)
                filter_related_words_num = sum(len(related_phrase_data_1d) for related_phrase_data_2d in filtered_related_phrase_data_3d for related_phrase_data_1d in related_phrase_data_2d)
                
                await postgres_db.track_user_reminders_text_activity(user_id=user_id, 
                                                            sentences_num=sentences_num,
                                                            words_num = words_num,
                                                            related_words_num=related_words_num,
                                                            filter_related_words_num=filter_related_words_num,
                                                            prompt_tokens_num=response["prompt_tokens"],
                                                            completion_tokens_num=response["completion_tokens"],
                                                            response_time=response_time
                                                            )
    except (WebSocketDisconnect, ConnectionResetError, RuntimeError) as e:
        pass # connection lost
    except Exception as e:
        error_logger.error(traceback.format_exc())
        await websocket.send_json(RemindersTextResponse(status="error", error=str(e), data=RemindersTextResponseData(tab_id=tab_id, request_id=request_id, is_final=False, reminders_text_data=[])).model_dump())


########################## Main ########################## 

async def main():
    await qdrant_db.create_collections_if_not_exist()
    await postgres_db.create_tables_if_not_exist()

    print("Starting FastAPI server")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    asyncio(main())