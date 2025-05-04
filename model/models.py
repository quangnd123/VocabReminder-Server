from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar, Literal

T = TypeVar("T")  # Generic Type for Responses

class BaseResponse(BaseModel, Generic[T]):
    status: Literal["success", "error"]
    error: Optional[str] = None
    data: Optional[T] = None


# ----------------- PHRASE-----------------
class PhraseData(BaseModel):
    id: str 
    phrase: str
    phrase_idx: int
    sentence: str
    language: str

class GetPhrasesRequest(BaseModel):
    user_id: str

class GetPhrasesResponse(BaseResponse[List[PhraseData]]):
    pass

class CreatePhraseRequest(BaseModel):
    user_id: str
    phrase: str
    phrase_idx: Optional[int]= None
    sentence: Optional[str]= None
    language: Optional[str] = None

class CreatePhraseResponse(BaseResponse[PhraseData]):
    pass

class DeletePhrasesRequest(BaseModel):
    phrase_ids: List[str]

class DeletePhrasesResponse(BaseResponse[None]):
    pass

class TranslatePhraseRequest(BaseModel):
    user_id: str
    phrase: str
    phrase_idx: int
    sentence: str
    translate_language: str

class TranslatePhrasesResponse(BaseResponse[str]):
    pass

# ----------------- Reminders Text -----------------
class RemindersTextRequest(BaseModel):
    tab_id: int
    request_id: int
    user_id: str
    reading_languages: List[str]
    llm_response_language: str
    learning_languages: List[str]
    sentences: List[str]

class ReminderTextData(BaseModel):
    sentence: str
    word: str
    word_idx: int
    related_phrase: str
    related_phrase_sentence: str
    reminder: str

class RemindersTextResponseData(BaseModel):
    tab_id: int
    request_id: int
    is_final: bool
    reminders_text_data: List[ReminderTextData]

class RemindersTextResponse(BaseResponse[RemindersTextResponseData]):
    pass


# ----------------- User -----------------
class UpdateUserRequest(BaseModel):
    id: str
    name: Optional[str] = None
    reading_languages: List[str]
    learning_languages: List[str]
    llm_response_language: Optional[str] = None
    unallowed_urls: List[str]

class User(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    reading_languages: List[str]
    learning_languages: List[str]
    llm_response_language: Optional[str] = None
    unallowed_urls: List[str]

class UpdateUserResponse(BaseResponse[User]):
    pass