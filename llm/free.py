import re 
import asyncio
import sys
import os 
from pathlib import Path
import time
from mistralai import Mistral

from dotenv import load_dotenv
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")
from model.models import TranslatePhraseRequest

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
logger = get_logger(__name__, "freeLLM.log")


class FreeLLM():
    def __init__(self):
        self.batch_number = 50
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.model = "mistral-large-latest"

    async def send_prompt(self, prompt: str):
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

    def get_reminders_text_prompt_input(self, sentence_data_1d: list) -> str:
        result = []
        formatted_text = ""
        id = 1
        for sentence_data in sentence_data_1d:
            for word_data, related_phrase_data_1d in zip(sentence_data['word_data_1d'], sentence_data['related_phrase_data_2d']):
                for related_phrase_data in related_phrase_data_1d:
                    if word_data['ignore'] == True:
                        continue
                    formatted_text += f"{id} # {related_phrase_data.payload['phrase']} # {word_data['word']} # {related_phrase_data.payload['sentence']} # {sentence_data['sentence']}\n"
                    
                    if id % self.batch_number == 0:
                        result.append(formatted_text)
                        formatted_text = ""
                    id+=1
        if formatted_text:
            result.append(formatted_text)
        return result
    
    def parse_data(self, llm_answer, sentence_data_1d):
        lines = [line for line in llm_answer.split("\n") if line]
        pattern = r"^#\s+(\d+)\s+#\s+(.+)$"

        data_id = 1
        line_idx = 0
        for sentence_data in sentence_data_1d:
            for word_data, related_phrase_data_1d in zip(sentence_data['word_data_1d'], sentence_data['related_phrase_data_2d']):
                if word_data['ignore'] == True:
                    continue
                for related_phrase_data in related_phrase_data_1d:
                    # parse line
                    line = lines[line_idx]
                    match = re.match(pattern, line)
                    if match:
                        id = int(match.group(1))
                        reminder = match.group(2).strip() if match.group(2).strip() else None
                        if id == data_id:
                            line_idx+=1
                            if reminder != None:
                                related_phrase_data.payload["reminder"] = reminder
                    else:
                        line_idx+=1 

                    data_id+=1

                    if line_idx >= len(lines):
                        return

    def get_reminders_text_prompt_template(self, llm_response_language: str) -> str:
        prompt = f"""
You are an intelligent language learning assistant, specializing in connect their new vocabulary words with familiar ones, which helps them internalize new vocabulary more effectively and develop a deeper understanding of word relationships.

# Instruction:

## Given a list of inputs, each in this format:
<ID> # <memorized_vocab> # <seen_word> # <memorized_vocab_context> # <seen_word_context>

## For each input, find connection between <memorized_vocab> and <seen_word> based on the context of <memorized_vocab_context> and <seen_word_context>.
- Connections must be clear, logical, senseful.
- Possible Connections include:
    * Etymology: Eg. words like "audible", "auditorium", and "audience" share the root word "aud" (from Latin "audire" meaning to hear) all directly related to hearing.
    * Thematically-linked: Words strongly related to the same concept, context, or experience (e.g., *gloves - hands - winter* because gloves are worn on hands in winter). Explain the semantic or practical relationship between them.
    * Same Lemma: Words sharing a common base with a direct and understandable shift in meaning or function due to prefixes/suffixes (e.g., *play - playful*) .
    * Collocations: Words that form common and significant pairings (e.g., seeing "heavy" might remind of "heavy rain" if "rain" is memorized). 
    * Other Connections: Synonyms, Antonyms, Hyponyms/Hypernyms, or any other clear, logical, and senseful connection

## After finding a connection, give a 2-digit confidence score from 0 to 1,
where 1 is the highest confidence, connection is obvious, logical, senseful. 0 is where the connection is forced, illogical, or nonsensical.
    
## Come up with a reminder in Vietnamese for the user to remember the connection. 
The reminder must be concise, natural, easy-to-understand and user-friendly. 
It should help the user improve retention of <memorized_vocab> with <seen_word>.

## Provide output for only input with confidence score >= 0.9 in the following format (No explanation, no extra text): 
# <ID> # <reminder>


# Examples: (Reminders in Vietnamese)

Input:
3 # import # deport # They will import rice next year. # I was deport from my home country.

Output:
3 # "deport" và "import" đều chứa gốc "port" có nghĩa là "mang, chở". "import" là mang hàng hóa vào (in), còn "deport" là mang người ra (de) khỏi đất nước. Cùng gốc "port" nhưng hai hướng hành động ngược nhau.

Input:
18 # predict # dictate # Scientists predict the weather. # The boss dictated the memo to his secretary.

Output:
18 # Chữ "dictate" có cùng gốc "dict" (nghĩa là "nói, tuyên bố") với từ "predict". "predict" là nói trước (pre) điều gì sẽ xảy ra, còn "dictate" là nói để người khác làm theo.

Input:
25 # light # photosynthesis # The room is full of light. # Photosynthesis is essential for plant growth.

Output:
25 # "photo" trong "photosynthesis" có nghĩa là "light" ("ánh sáng") đó! "photosynthesis" là quá trình cây xanh sử dụng "light" để tạo ra thức ăn.
**END OF EXAMPLES**

# Now, generate output for this input: (reminders language is in {llm_response_language})

"""

        return prompt

    async def get_reminders_text(self, sentence_data_1d: list, llm_response_language: str) -> str:
        prompt_template = self.get_reminders_text_prompt_template(llm_response_language)
        prompt_inputs = self.get_reminders_text_prompt_input(sentence_data_1d=sentence_data_1d)
        
        tasks = []
        for prompt_input in prompt_inputs:
            prompt = (prompt_template + prompt_input).strip()
            logger.info(prompt)
            tasks.append(self.send_prompt(prompt=prompt))
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        response_time = time.time() - start_time
        
        answer = ""
        prompt_tokens=0
        completion_tokens=0
        for response in responses:
            answer += response.choices[0].message.content.strip() + "\n"
            prompt_tokens += response.usage.prompt_tokens
            completion_tokens += response.usage.completion_tokens
        answer = answer.strip()
        logger.info(answer)
        
        self.parse_data(llm_answer=answer, sentence_data_1d=sentence_data_1d)
        return prompt_tokens, completion_tokens, response_time
        

    async def translate_phrase(self, translate_phrase_request: TranslatePhraseRequest):
        prompt = f"""Translate a phrase in context. You'll receive:
- A phrase
- The full sentence containing that phrase
- The phrase's character index in the sentence
- A target language: {translate_phrase_request.translate_language}

Your tasks:
1. The phrase can have many meanings. Translate the phrase into {translate_phrase_request.translate_language} with the meaning that fit its sentence(context).
2. Translate the sentence naturally into {translate_phrase_request.translate_language}.
3. Explain the phrase's definition briefly in its original language, based on its meaning in the sentence.

FOLLOW THE OUTPUT FORMAT STRICTLY. Do not add anything else.
There are 3 sections in output. Section 1 and 2 must be in {translate_phrase_request.translate_language} including the section tiltes, section 3 must be in the phrase's language including the section tilte:
Output format:
1. Phrase meaning: <Phrase translated>
2. Sentence meaning: <Sentence translated>
3. Definition: <Explanation in phrase's language>

Example input:
Phrase: "努力"  
Index: 3  
Sentence: "我们每天都在努力工作。"  
Target language: Vietnamese

Example output: 
1. Nghĩa của từ: nỗ lực
2. Nghĩa của câu: Mỗi ngày chúng tôi đều nỗ lực làm việc.
3. 定义: “努力”是指在某件事情上付出很多心力或尽力去做。

Now your input:
Phrase: "{translate_phrase_request.phrase}"  
Index: {translate_phrase_request.phrase_idx}  
Sentence: "{translate_phrase_request.sentence}"  
Target language: {translate_phrase_request.translate_language}
"""
        response = await self.send_prompt(prompt=prompt, model = translate_phrase_request.free_llm)
        content = response.choices[0].message.content
        return content
    
    async def create_sentence(self, phrase: str, language: str, model: str) -> str:
        prompt = f"""Give me a NATURAL and CONCISE sentence in {language} that includes the phrase: "{phrase}" exactly as written, do not change its casing. 
        Only output the sentence. No explanation or extra text."""
        response = await self.send_prompt(prompt=prompt, model = model)
        content = response.choices[0].message.content
        return content