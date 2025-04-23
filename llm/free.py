import httpx
import re 
import asyncio
import json
import sys
import os 
from pathlib import Path
import time
from dotenv import load_dotenv
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

base_dir = os.path.dirname(__file__)

# common env
common_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=common_env_path)
env = os.getenv("ENV")
# local/prod env
env_path =""
if env == "local":
    env_path = Path(__file__).parent.parent / ".env.local"
elif env =="production":
    env_path = Path(__file__).parent.parent / ".env.production"
load_dotenv(dotenv_path=env_path)

open_router_API = os.getenv("OPENROUTER_API")
project_name = os.getenv("PROJECT_NAME")
client_url = os.getenv("CLIENT_URL")

from logger.logger import get_logger
logger = get_logger(__name__, "freeLLM.log")


class FreeLLM():
    def __init__(self):
        self.batch_number = 50

    async def send_prompt(self, prompt: str, model: str):
        headers = {
            "Authorization": f"Bearer {open_router_API}",
            "Content-Type": "application/json",
            "HTTP-Referer": f"{client_url}",  # Optional: replace or remove
            "X-Title": f"{project_name}",     # Optional: replace or remove
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:  # 10 seconds timeout
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error: {e}") from e
        except json.JSONDecodeError:
            raise RuntimeError(f"Invalid JSON received: {response.text}")

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
        pattern = r"(\d+)\s+#\s*([^#]*)#\s*(.*)"

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
                        relation = match.group(2).strip() if match.group(2).strip() else None
                        reminder = match.group(3).strip() if match.group(3).strip() else None
                        if id == data_id:
                            line_idx+=1
                            if relation != None and reminder != None:
                                related_phrase_data.payload["reminder"] = reminder
                    else:
                        line_idx+=1 

                    data_id+=1

                    if line_idx >= len(lines):
                        return

    def get_reminders_text_prompt_template(self, reminding_language: str):
        prompt = f"""
## Task:
You're helping a language learner recall vocabulary by linking it with a word they encounter while browsing.

**Input Format:**
<ID> # <memorized_vocab> # <seen_word> # <memorized_vocab_context> # <seen_word_context> 

**Output Format:**
<ID> # <CONNECTION_TYPE> # <Concise, vivid mnemonic reminder in {reminding_language} that clearly connects the two words and their contexts. Include both words and refer to their original sentences.>

**Instructions:**
- For each line, find a strong and understandable link between the word the user saw and the vocabulary they’re trying to remember.
- Use semantic relationships such as: Synonym, Antonym, Hypernym, Hyponym, Meronym, Holonym, Causality, Troponym, Complementarity, Etymology, or Collocation.
- You may also use grammar links (e.g. same root), emotional cues, visual imagery, or shared phrases.
- Use the provided contexts to disambiguate meanings and inspire the mnemonic.
- If the vocabulary word the **user** wants to memorize has already appeared in the sentence seen, emphasize repeated exposure in a new context to reinforce memory.
- The mnemonic reminder should include:
  - Both the seen word and the vocab word (in their original form),
  - A vivid mental connection in {reminding_language},
  - Reference to both contexts to make the association stronger.
- DO NOT include outputs for pairs without a strong link. Only generate output when there's a direct or vivid link that would help the user **recall the vocab word** later.
- DO NOT write placeholders like "EMPTY". Just skip those IDs.
- DO NOT explain your reasoning, DO NOT ADD extra text or headers.
- Keep output format strict:  
  <ID> # <CONNECTION_TYPE> # <Mnemonic reminder>

**Examples:**

1 # The # rainbow # The sun rises in the east. # A rainbow appeared after the rain.
→ 1 # No relation

2 # Hot # Cold # The soup was too hot to drink. # She preferred her coffee cold in summer.  
→ 2 # Antonym # 'Hot' và 'Cold' là hai cực đối lập: súp nóng không uống được, còn cà phê lạnh lại được ưa chuộng vào mùa hè. Hình ảnh nóng-lạnh giúp bạn nhớ rõ hơn.

5 # Tree # Leaf # The tree swayed gently in the wind. # A single leaf drifted to the ground.  
→ 5 # Meronym # 'Leaf' là một phần của 'Tree'. Khi thấy cây đung đưa trong gió, bạn nhớ đến chiếc lá rơi – gắn kết hình ảnh tự nhiên.

7 # Smoking # Lung cancer # My dad loves smoking. # My mother has a lung cancer.  
→ 7 # Causality # 'Smoking' có thể dẫn đến 'lung cancer'. Hình ảnh người cha hút thuốc và người mẹ bệnh là lời nhắc mạnh mẽ về mối liên hệ nhân quả.

**END OF EXAMPLES**


**Now, generate output for this input:**

"""

        return prompt

    async def get_reminders_text(self, sentence_data_1d: list, reminding_language: str, free_llm: str ):
        prompt_template = self.get_reminders_text_prompt_template(reminding_language)
        prompt_inputs = self.get_reminders_text_prompt_input(sentence_data_1d=sentence_data_1d)
        
        tasks = []
        for prompt_input in prompt_inputs:
            prompt = (prompt_template + prompt_input).strip()
            logger.info(prompt)
            tasks.append(self.send_prompt(prompt=prompt, model=free_llm))
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        response_time = time.time() - start_time
        
        answer = ""
        prompt_tokens=0
        completion_tokens=0
        for response in responses:
            answer += response["choices"][0]["message"]["content"].strip() + "\n"
            prompt_tokens += response["usage"]["prompt_tokens"]
            completion_tokens += response["usage"]["completion_tokens"]
        answer = answer.strip()
        logger.info(answer)
        
        self.parse_data(llm_answer=answer, sentence_data_1d=sentence_data_1d)
        return prompt_tokens, completion_tokens, response_time
        
