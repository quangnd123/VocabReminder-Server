import httpx
import re 
import asyncio
from typing import List
import pprint
import json
class FreeLLM():
    def __init__(self):
        self.API_KEY = "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"
        #self.model = "google/gemini-2.0-flash-lite-preview-02-05:free"
        self.model = "qwen/qwen2.5-vl-32b-instruct:free"
        self.batch_number = 15
        self.system_prompt = """
You are an intelligent language assistant that helps users memorize vocabulary by finding meaningful connections between words in a given text and stored vocabulary words.
"""
    async def send_prompt(self, prompt, model, system_prompt=None):
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
            for (word_data, related_phrase_data_1d) in zip(sentence_data['word_data_1d'], sentence_data['related_phrase_data_2d']):
                for related_phrase_data in related_phrase_data_1d:
                    formatted_text += f"{id} # {word_data['word']} # {related_phrase_data.payload['phrase']} # {sentence_data['sentence']} # {related_phrase_data.payload['sentence']}\n"
                    id+=1
                    if id == self.batch_number:
                        result.append(formatted_text)
                        formatted_text = ""
        return result
    
    def parse_data(self, llm_answer, sentence_data_1d):
        lines = [line for line in llm_answer.split("\n") if line]
        pattern = r"(\d+)\s+#\s*([^#]*)#\s*(.*)"

        data_id = 1
        line_idx = 0
        for sentence_data in sentence_data_1d:
            for related_phrase_data_1d in sentence_data['related_phrase_data_2d']:
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
                        print("PARSING ERROR")
                        print(line)
                        line_idx+=1 

                    data_id+=1

                    if line_idx >= len(lines):
                        return

    def get_reminders_text_prompt_template(reminding_language: str):
        prompt =  f"""
## Task:
You are assisting language learners reading words online with a vocabulary list of vocab they want to memorize.
** Input Format:
<ID> # <word users see> # <vocab users want to memorize> # <word_context> # <vocab_context>

** Output Format:
<ID same as input> # UNDERSTANDABLE connection between word and vocab # Concise, vivid mnemonic that naturally links the two words.

- For each pair of word, find a meaningful connection to the phrase users want to memorize. 
- Possible connection examples: Synonym, Antonym, Hypernym, Hyponym, Meronym, Holonym, Causality, Troponym, Complementarity, Etymology, Collocation. 
- You can be creative for connections
- Context is provided for both word and vocab to clarify meaning.
- DO NOT generate output for cases where no strong, understandable connection exists. DO NOT force weak or vague links. If there is NO valid connection, do NOT generate output for that ID at all. DO NOT output "EMPTY" or any placeholder. JUST SKIP IT COMPLETELY.
- Follow the exact output format to ensure proper parsing with Python.
- Allowed Collocation example:
adverb + adjective: completely satisfied (NOT downright satisfied)
adjective + noun: excruciating pain (NOT excruciating joy)
noun + noun: a surge of anger (NOT a rush of anger)
noun + verb: lions roar (NOT lions shout)
verb + noun: commit suicide (NOT undertake suicide)
verb + expression with preposition: burst into tears (NOT blow up in tears)
verb + adverb: wave frantically (NOT wave feverishly)
- Provide the reminders in {reminding_language}, but keep eveything in the input in its own language.

**EXAMPLES:**

Input:
2 # Hot # Cold # The soup was too hot to drink. # She preferred her coffee cold in summer.
Output:
2 # Antonym # 'Hot' and 'Cold' are opposites. If something is hot, it has a high temperature, but if it’s cold, it has a low temperature.

Input:
3 # Rose # Flower # She received a rose on Valentine's Day. # The garden was full of beautiful flowers.
Output:
3 # Hypernym # A 'Rose' is a type of 'Flower'. Flowers include roses, tulips, and daisies.

Input:
5 # Tree # Leaf # The tree swayed gently in the wind. # A single leaf drifted to the ground.
Output: 
5 # Meronym # A 'Leaf' is a part of a 'Tree'. Trees have leaves, branches, and bark.

Input:
7 # Smoking # Lung cancer # My dad loves smoking # My mother has a lung cancer.
Output:
7 # Causality # Smoking can cause lung cancer and other health problems.

Input:
9 # Married # Single # She has been married for five years. # He is still single and looking for a partner.
Output:
9 # Complementarity # 'Married' and 'Single' are mutually exclusive. If someone is married, they are not single, and vice versa.

Input:
13 # Fast # Food # He prefers fast food over home-cooked meals. # Fast food is often unhealthy.
Output:
13 # Collocation # 'Fast' and 'Food' commonly appear together. 'Fast food' means quickly prepared meals like burgers and fries.

Input:
10 # Cancer # Love # I have cancer. # I love you.
Output:
10 # #

Input:
13 # Do # Yes I do # DO # Do you want this?
11 # Likes # Like # She likes me. # I like you. 
12 # Import # Export # The country imports a lot of rice. # They export high-quality coffee beans.
Output:
13 # Identical # Hey, you want to memorize "do" right? Here it is.
11 # Same Root # "Likes" is the third-person singular present tense form of the verb "like"
12 # Same root # 'Import' and 'Export' share the root 'port,' meaning 'carry.' Import = IN (carry into a country), Export = EX (carry out of a country).

**END OF EXAMPLES**

Now, Create output for this input:
Input:

"""
        return prompt

    async def get_reminders_text(self, sentence_data_1d: list, reminding_language: str ):
        prompt_template = self.get_reminders_text_prompt_template(reminding_language)
        prompt_inputs = self.get_reminders_text_prompt_input(sentence_data_1d=sentence_data_1d)
        
        tasks = []
        for prompt_input in prompt_inputs:
            prompt = (prompt_template + prompt_input).strip()
            if prompt:
                tasks.append(self.send_prompt(prompt=prompt))
        responses = await asyncio.gather(*tasks)
        
        answer = ""
        for response in responses:
            answer += response["choices"][0]["message"]["content"].strip() + "\n"
        answer = answer.strip()

        self.parse_data(llm_answer=answer, sentence_data_1d=sentence_data_1d)
        return 
        
