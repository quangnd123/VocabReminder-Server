def get_reminders_text_prompt_template(llm_response_language: str) -> str:
        prompt = f"""
You are an intelligent language learning assistant, specializing in connect their new vocabulary words with familiar ones, which helps them internalize new vocabulary more effectively and develop a deeper understanding of word relationships.

# Instruction:

Step 1: Given a list of inputs, each in this format:
<ID> # <memorized_vocab> # <seen_word> # <memorized_vocab_context> # <seen_word_context>

Step 2: For each input, find connection between <memorized_vocab> and <seen_word> based on the context of <memorized_vocab_context> and <seen_word_context>.
- Connections must be clear, logical, senseful.
- Possible Connections include:
    * Itself: <seen_word> == <memorized_vocab>, remind users of the meaning of <memorized_vocab>: "Do you still remember <memorized_vocab> which means ...?" in {llm_response_language}.
    * Etymology: Example Reminder: "audible", "auditorium", and "audience" share the root word "aud" (from Latin "audire" meaning to hear) all directly related to hearing.
    * Thematically-linked: Words strongly related to the same concept, context, or experience (e.g., *gloves - hands - winter* because gloves are worn on hands in winter). Explain the semantic or practical relationship between them.
    * Same Lemma: Words sharing a common base with a direct and understandable shift in meaning or function due to prefixes/suffixes (e.g., *play - playful*) .
    * Collocations: Words that form common and significant pairings (e.g., seeing "heavy" might remind of "heavy rain" if "rain" is memorized). 
    * Other Connections: Synonyms, Antonyms, Hyponyms/Hypernyms, or any other clear, logical, and senseful connection

Step 3: After finding a connection, give a 2-digit confidence score from 0 to 1,
where 1 is the highest confidence, connection is strong, obvious, logical, senseful. 0 is where the connection is forced, weak, vague, illogical, or nonsensical.
    
Step 4: Come up with a reminder in {llm_response_language} the connection, so that users improve retention of <memorized_vocab> with <seen_word>
The reminder must be concise, logical, natural, easy-to-understand and user-friendly. 

Step 5: Provide output for only input with confidence score >= 0.9 in the following format (No explanation, no extra text). 
<ID> # <reminder>

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

# Now, generate output for this input: (reminders language is {llm_response_language})

"""

        return prompt


def get_generate_sentence_prompt(phrase: str, language: str) -> str:
    prompt = f"""Give me a NATURAL and CONCISE sentence in {language} that includes the phrase: "{phrase}" exactly as written, do not change its casing. 
Only output the sentence. No explanation or extra text."""
    return prompt


def get_translate_phrase_prompt(phrase: str, phrase_idx: int, sentence: str, phrase_language: str, response_language: str) -> str:
    prompt = f"""Translate a phrase in context. You'll receive:
- A phrase
- The full sentence containing that phrase
- The phrase's character index in the sentence
- A target language: {response_language}

Your tasks:
1. The phrase can have many meanings. Translate the phrase into {response_language} with the meaning that fit its sentence(context).
2. Translate the sentence naturally into {response_language}.
3. Explain the phrase's definition briefly in {phrase_language}, based on its meaning in the sentence.

FOLLOW THE OUTPUT FORMAT STRICTLY. Do not add anything else.
There are 3 sections in output. Section 1 and 2 must be in {response_language} including the section tiltes, section 3 must be in the {phrase_language} including the section tilte:
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
Phrase: "{phrase}"  
Index: {phrase_idx}  
Sentence: "{sentence}"  
Target language: {response_language}
"""
    return prompt