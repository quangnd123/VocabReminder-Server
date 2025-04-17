import httpx
import re 
import asyncio
import json
import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

from logger.logger import get_logger
logger = get_logger(__name__, "freeLLM.log")

class FreeLLM():
    def __init__(self):
        self.API_KEY = "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"
        #self.model = "google/gemini-2.0-flash-lite-preview-02-05:free"
        #self.model = "qwen/qwen2.5-vl-32b-instruct:free"
        self.model = "google/gemini-2.0-flash-exp:free"
        self.batch_number = 50
        self.system_prompt = """
You are an intelligent language assistant that helps users memorize vocabulary by finding meaningful connections between words in a given text and stored vocabulary words.
"""
    async def send_prompt(self, prompt, model=None, system_prompt=None):
        if model == None:
            model = self.model
        if system_prompt == None:
            system_prompt = self.system_prompt
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
                    "X-Title": "<YOUR_SITE_NAME>",  # Optional
                },
                json={  # Use `json` instead of `data=json.dumps(...)`
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                },
            )
            if response.status_code != 200:
                print(f"Error {response.status_code}: {response.text}")
                return None

            try:
                return response.json()
            except json.JSONDecodeError:
                print("Invalid JSON received:", response.text)
                return None

    def get_reminders_text_prompt_input(self, sentence_data_1d: list) -> str:
        result = []
        formatted_text = ""
        id = 1
        for sentence_data in sentence_data_1d:
            for word_data, related_phrase_data_1d in zip(sentence_data['word_data_1d'], sentence_data['related_phrase_data_2d']):
                for related_phrase_data in related_phrase_data_1d:
                    if word_data['ignore'] == True:
                        continue
                    formatted_text += f"{id} # {word_data['word']} # {related_phrase_data.payload['phrase']} # {sentence_data['sentence']} # {related_phrase_data.payload['sentence']}\n"
                    
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
You're helping a language learner recall vocabulary by linking it with real-world usage they encounter while browsing.

**Input Format:**
<ID> # <word users see> # <vocab users want to memorize> # <word_context> # <vocab_context>

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

    async def get_reminders_text(self, sentence_data_1d: list, reminding_language: str ):
        prompt_template = self.get_reminders_text_prompt_template(reminding_language)
        prompt_inputs = self.get_reminders_text_prompt_input(sentence_data_1d=sentence_data_1d)
        
        tasks = []
        for prompt_input in prompt_inputs:
            prompt = (prompt_template + prompt_input).strip()
            logger.info(prompt)
            tasks.append(self.send_prompt(prompt=prompt, model=self.model))
        responses = await asyncio.gather(*tasks)
        
        answer = ""
        for response in responses:
            answer += response["choices"][0]["message"]["content"].strip() + "\n"
        answer = answer.strip()
        logger.info(answer)
        self.parse_data(llm_answer=answer, sentence_data_1d=sentence_data_1d)
        return 
        
