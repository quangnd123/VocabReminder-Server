import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

import uvicorn
import os 

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import *
from qdrant import AsyncQdrant
from postgresql import PostgreSQLDatabase
from llm.free import FreeLLM
# from filter import RelatedPhrasesFilter
from test.data import word_sentence_pairs
from embedding import get_embedders
from logger.logger import get_logger
from fasttext_092.language_detection import detect_language
from pathlib import Path

########################## INIT ##########################
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
postgres_db_url = os.getenv("POSTGRES_DATABASE_URL")
assert postgres_db_url
postgres_db = PostgreSQLDatabase(db_url=postgres_db_url)

logger = get_logger(__name__, "server.log")

freeLLM = FreeLLM()
# relatedPhrasesFilter = RelatedPhrasesFilter()
qdrant_db = AsyncQdrant(collection_name="test", embedding_model_dims=1024, path= "./qdrant_db", on_disk=True)

# FastAPI App
app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"chrome-extension://{os.getenv('BROWSER_EXTENSION_ID')}", os.getenv('CLIENT_URL')],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


########################## BROWSER EXTENSION ########################## 

@app.post("/create_phrase")
async def create_phrase(create_phrase_request: CreatePhraseRequest):
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
async def get_phrases(get_phrase_request: GetPhrasesRequest):
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
async def delete_phrases(delete_phrases_request: DeletePhrasesRequest):
    try:
        await qdrant_db.delete_1d(id_1d=delete_phrases_request.phrase_ids)
        return DeletePhrasesResponse(status="success")
    except Exception as e:
        return DeletePhrasesResponse(status="error", error=str(e))

# @app.post("/reminders-text")
# async def get_reminders_texts(reminders_text_request: RemindersTextRequest):
#     try:
#         user_id = reminders_text_request.user_id
#         reading_languages = reminders_text_request.reading_languages
#         reminding_language = reminders_text_request.reminding_language
#         learning_languages = reminders_text_request.learning_languages

#         sentences = []
#         sentences_language = []
#         for sentence in reminders_text_request.sentences:
#             sentence_language = detect_language(sentence)
#             if sentence_language in reading_languages: 
#                 sentences.append(sentence)
#                 sentences_language.append(sentence_language)
        
#         word_data_2d = [] #[num_sentences, num_words] an element is a dict
#         word_embedding_2d = [] #[num_sentences, num_words] an element is a list of float
#         # all embedders use the same token embedding regardless of language
#         token_embedding_2d = get_embedders("eng").get_token_embedding_2d(sentences=sentences) #[num_sentences, num_tokens] an element is a list of float
#         for token_embedding_1d, sentence, sentence_language in zip(token_embedding_2d, sentences, sentences_language):
#             embedder = get_embedders(sentence_language)
#             word_data_1d = embedder.get_word_data_1d(sentence=sentence)
#             word_embedding_1d = embedder.get_word_embedding_1d(sentence=sentence, word_data_1d=word_data_1d, token_embedding_1d=token_embedding_1d)
#             word_data_2d.append(word_data_1d)
#             word_embedding_2d.append(word_embedding_1d.tolist())

#         related_phrase_data_3d = await qdrant_db.search_3d(query=word_embedding_2d, 
#                                                            filters={"user_id": user_id, 
#                                                                     "language": {"in": learning_languages}}) #[num_sentences, num_words, num_related_words] an element is a ScorePoint
#         related_phrase_data_3d = relatedPhrasesFilter.filter(related_phrase_data_3d=related_phrase_data_3d)

#         sentence_data_1d = []
#         for sentence, word_data_1d, related_phrase_data_2d in zip(sentences, word_data_2d, related_phrase_data_3d):
#             sentence_data_1d.append({"sentence": sentence, "word_data_1d": word_data_1d, "related_phrase_data_2d": related_phrase_data_2d})       

#         prompt = freeLLM.get_reminders_text_prompt_input(sentence_data_1d, remind_language = reminding_language)
#         logger.info("PROMPT: ")
#         logger.info(prompt)
#         response = await freeLLM.send_prompt(prompt=prompt)
#         answer = response["choices"][0]["message"]["content"]

#         freeLLM.parse_data(llm_answer=answer, sentence_data_1d=sentence_data_1d)

#         data = relatedPhrasesFilter.sample_reminder(sentence_data_1d=sentence_data_1d)
#         logger.info("ANSWER: ")
#         logger.info(answer)
#         return RemindersTextResponse(status="success", data=data)
#     except Exception as e:
#         raise RemindersTextResponse(status="error", error=str(e))





########################## CLient ##########################

@app.post("/update_user")
async def update_user(updated_user: UpdateUserRequest):
    try:
        user = await postgres_db.update_user(user_id=updated_user.id, 
                                       name=updated_user.name, 
                                       reading_languages=updated_user.reading_languages,
                                       learning_languages=updated_user.learning_languages,
                                       reminding_language=updated_user.reminding_language)
        if not user: 
            return UpdateUserResponse(status="error", error="User not found")
        
        return UpdateUserResponse(status="success", data=User(id=user.id, 
                                                              name=user.name, 
                                                              email=user.email, 
                                                              reading_languages=user.reading_languages,
                                                              learning_languages=user.learning_languages,
                                                              reminding_language=user.reminding_language))
    except Exception as e:
        return UpdateUserResponse(status="error", error=str(e))


def main():
    print("Starting FastAPI server")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()