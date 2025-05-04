import re 
import sys
import os 
from pathlib import Path
from mistralai import Mistral
from dotenv import load_dotenv
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from model.models import TranslatePhraseRequest
from llm.prompts import get_reminders_text_prompt_template, get_generate_sentence_prompt, get_translate_phrase_prompt
from fasttext_092.language_detection import code_to_name, detect_language

base_dir = os.path.dirname(__file__)

# common env
common_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=common_env_path)
env = os.getenv("ENV")
# dev/prod env
env_path =""
if env == "development":
    env_path = Path(__file__).parent.parent / ".env.development"
elif env =="production":
    env_path = Path(__file__).parent.parent / ".env.production"
load_dotenv(dotenv_path=env_path)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

from logger.logger import get_logger
logger = get_logger("llm.free", "freeLLM.log")


class FreeLLM():
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model = "mistral-large-latest"

    async def llm_complete_async(self, prompt: str):
        chat_response = await self.client.chat.complete_async(
            model = self.model,
            temperature=0.5,
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )
        return chat_response
    
    async def llm_stream_async(self, prompt: str):
        chat_response = await self.client.chat.stream_async(
            model = self.model,
            temperature=0.5,
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )
        async for chunk in chat_response:
            if chunk.data is not None:
                yield chunk.data  

    def get_reminders_text_prompt_input(self, sentence_data_1d: list) -> str:
        formatted_text = ""
        id = 1
        for sentence_data in sentence_data_1d:
            for word_data, related_phrase_data_1d in zip(sentence_data['word_data_1d'], sentence_data['related_phrase_data_2d']):
                for related_phrase_data in related_phrase_data_1d:
                    formatted_text += f"{id} # {related_phrase_data.payload['phrase']} # {word_data['word']} # {related_phrase_data.payload['phrase_context']} # {word_data['word_context']}\n"
                    id+=1
        return formatted_text

    def get_reminders_text_data_factory(self, sentence_data_1d):
        def gen():
            for sentence_data in sentence_data_1d:
                word_data_1d = sentence_data["word_data_1d"]
                related_phrase_data_2d = sentence_data["related_phrase_data_2d"]
                for word_data, related_phrase_data_1d in zip(word_data_1d, related_phrase_data_2d):
                    for related_phrase_data in related_phrase_data_1d:
                        yield (sentence_data["sentence"], word_data, related_phrase_data)

        element_iter = gen()
        current_id = 1

        def get_element_by_id(target_id: int):
            nonlocal current_id
            try:
                while current_id < target_id:
                    next(element_iter)
                    current_id += 1
                if current_id == target_id:
                    element = next(element_iter)
                    current_id += 1
                    return element
            except StopIteration:
                return None  # No more elements

        def get_reminders_text_data(lines: list[str]):
            pattern = r"^(\d+)\s+#\s+(.+)$"
            result = []
            for line in lines:
                match = re.match(pattern, line)
                if match:
                    id = int(match.group(1))
                    reminder = match.group(2).strip() if match.group(2).strip() else None
                    if reminder != None:
                        element = get_element_by_id(id)
                        if element is None:
                            continue 
                        sentence, word_data, related_phrase_data = element
                        word = word_data["word"]
                        word_idx = word_data["word_idx"]
                        related_phrase = related_phrase_data.payload["phrase"]
                        related_phrase_sentence = related_phrase_data.payload["sentence"]
                        data = {
                            "sentence": sentence,
                            "word": word,
                            "word_idx": word_idx,
                            "related_phrase": related_phrase,
                            "related_phrase_sentence": related_phrase_sentence,
                            "reminder":reminder
                        }
                        result.append(data)
            return result

        return get_reminders_text_data

    async def get_reminders_text(self, sentence_data_1d: list, llm_response_language: str):
        prompt_template = get_reminders_text_prompt_template(code_to_name(llm_response_language))
        prompt_input = self.get_reminders_text_prompt_input(sentence_data_1d=sentence_data_1d)
        if not prompt_input:
            yield {"end": True, "reminders_text_data": [], "prompt_tokens": 0, "completion_tokens": 0, "response_time": 0}
            return 
        
        prompt = prompt_template + prompt_input
        logger.info(prompt_input)
        buffer = ""
        lines = []
        get_reminders_text_data = self.get_reminders_text_data_factory(sentence_data_1d)
        
        async for response in self.llm_stream_async(prompt=prompt):
            if response.choices[0].delta.content:
                buffer += response.choices[0].delta.content
                # print(response.choices[0].delta.content, end="", flush=True)
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    lines.append(line.strip())

            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                data = get_reminders_text_data([buffer])
                yield {"end": True, "reminders_text_data": data, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}
                return
            
            if lines:
                data = get_reminders_text_data(lines)
                yield {"end": False, "reminders_text_data": data}
                lines.clear()
        

    async def translate_phrase(self, translate_phrase_request: TranslatePhraseRequest):
        response_language = code_to_name(translate_phrase_request.translate_language)
        phrase_language_code = detect_language(translate_phrase_request.phrase)
        if phrase_language_code == "unknown":
            phrase_language = "phrase's language"
        else:
            phrase_language = code_to_name(phrase_language_code)

        prompt = get_translate_phrase_prompt(
            phrase=translate_phrase_request.phrase,
            phrase_idx=translate_phrase_request.phrase_idx,
            sentence=translate_phrase_request.sentence,
            phrase_language=phrase_language,
            response_language=response_language
        )
        response = await self.llm_complete_async(prompt=prompt)
        content = response.choices[0].message.content
        return content
    
    async def create_sentence(self, phrase: str, language: str) -> str:
        language = code_to_name(language)
        prompt = get_generate_sentence_prompt(phrase=phrase, language=language)
        response = await self.llm_complete_async(prompt=prompt)
        content = response.choices[0].message.content
        return content