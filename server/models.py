from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar

T = TypeVar("T")  # Generic Type for Responses

class BaseResponse(BaseModel, Generic[T]):
    status: str  # "success" or "error"
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
    phrase_idx: int
    sentence: str
    language: Optional[str] = None

class CreatePhraseResponse(BaseResponse[PhraseData]):
    pass

class DeletePhrasesRequest(BaseModel):
    phrase_ids: List[str]

class DeletePhrasesResponse(BaseResponse[None]):
    pass

# ----------------- Reminders Text -----------------
class RemindersTextRequest(BaseModel):
    user_id: str
    reading_languages: List[str]
    reminding_language: str
    learning_languages: List[str]
    sentences: List[str]

class RemindersTextResponseSentenceData(BaseModel):
    word: str
    word_idx: int
    related_phrase: str
    related_phrase_sentence: str
    reminder: str

class RemindersTextResponseData(BaseModel):
    sentence: str
    reminders_data: List[RemindersTextResponseSentenceData]

class RemindersTextResponse(BaseResponse[List[RemindersTextResponseData]]):
    pass



# ----------------- User -----------------
class UpdateUserRequest(BaseModel):
    id: str
    name: str|None
    reading_languages: List[str]
    learning_languages: List[str]
    reminding_language: Optional[str] = None
    free_llm: Optional[str] = None
    unallowed_urls: List[str]

class User(BaseModel):
    id: str
    name: str|None
    email: str|None
    reading_languages: List[str]
    learning_languages: List[str]
    reminding_language: Optional[str] = None
    free_llm: Optional[str] = None
    unallowed_urls: List[str]

class UpdateUserResponse(BaseResponse[User]):
    pass


class GetFreeLLMsResponse(BaseResponse[list[str]]):
    pass