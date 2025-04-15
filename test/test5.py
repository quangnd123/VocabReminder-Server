import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

from llm.free import FreeLLM
import logging
import time 

freeLLM = FreeLLM()
inputs = [
    "1 # Hot # Cold # The soup was too hot to drink. # She preferred her coffee cold in summer.",
    "2 # Rose # Flower # She received a rose on Valentine's Day. # The garden was full of beautiful flowers.",
    "3 # Tree # Leaf # The tree swayed gently in the wind. # A single leaf drifted to the ground.",
    "4 # Smoking # Lung cancer # My dad loves smoking. # My mother has lung cancer.",
    "5 # Married # Single # She has been married for five years. # He is still single and looking for a partner.",
    "6 # Fast # Food # He prefers fast food over home-cooked meals. # Fast food is often unhealthy.",
    "7 # Import # Export # The country imports a lot of rice. # They export high-quality coffee beans.",
    "8 # Doctor # Hospital # The doctor treated the patient. # The hospital was full of people.",
    "9 # Day # Night # We worked all day. # The stars were visible at night.",
    "10 # Sun # Moon # The sun was shining brightly. # The moon glowed in the dark sky.",
    "11 # Winter # Summer # Winter is cold and snowy. # Summer is hot and sunny.",
    "12 # Cat # Animal # She adopted a stray cat. # The animal shelter had many rescued pets.",
    "13 # Car # Vehicle # He bought a new car. # There were many vehicles on the road.",
    "14 # Teacher # School # The teacher explained the lesson. # The school was filled with students.",
    "15 # Book # Library # She borrowed a book from the library. # The library had thousands of books.",
    "16 # Rain # Umbrella # It started to rain suddenly. # She opened her umbrella to stay dry.",
    "17 # River # Water # The river flowed through the valley. # Water is essential for life.",
    "18 # Coffee # Caffeine # She needs coffee every morning. # Caffeine keeps her awake.",
    "19 # Sleep # Dream # He fell asleep quickly. # He had a strange dream last night.",
    "20 # Fire # Smoke # The fire burned the forest. # Thick smoke filled the air.",
    "21 # Ocean # Wave # The ocean stretched endlessly. # The waves crashed against the shore.",
    "22 # Phone # Call # She picked up the phone. # He made an important call.",
    "23 # Clock # Time # The clock struck midnight. # Time seemed to pass slowly.",
    "24 # Eye # Vision # His eyes were blue. # Good vision is important for reading.",
    "25 # Dog # Pet # They have a friendly dog. # Many people love having pets.",
    "26 # Bread # Butter # He spread butter on his bread. # The butter melted on the warm toast.",
    "27 # Mountain # Climb # They climbed the tall mountain. # Climbing requires strength and endurance.",
    "28 # Glass # Window # The glass was shattered. # The window was broken by the storm.",
    "29 # Fish # Water # The fish swam in the pond. # Water is their natural habitat.",
    "30 # Pen # Write # He grabbed a pen. # Writing is easier with a smooth pen.",
    "31 # Chair # Sit # She pulled out a chair. # He sat down to rest.",
    "32 # Teacher # Student # The teacher explained the lesson. # The students listened carefully.",
    "33 # Apple # Fruit # She ate a red apple. # Fruit is a healthy snack.",
    "34 # Snow # Cold # The snow covered the ground. # It was freezing cold outside.",
    "35 # Knife # Cut # He used a sharp knife. # Cutting onions made his eyes water.",
    "36 # Light # Dark # The light brightened the room. # The dark sky was full of stars.",
    "37 # Bicycle # Ride # He bought a new bicycle. # She loves to ride through the park.",
    "38 # Paper # Write # She wrote a note on paper. # Writing helps organize thoughts.",
    "39 # Lock # Key # The door had a lock. # She lost the key to her house.",
    "40 # Singer # Song # The singer performed beautifully. # The song was very emotional.",
    "41 # Milk # Dairy # He drank a glass of milk. # Dairy products are nutritious.",
    "42 # Baby # Cry # The baby started to cry. # She rocked the baby gently.",
    "43 # Clock # Alarm # His clock had a loud alarm. # The alarm woke him up.",
    "44 # Cloud # Rain # The clouds were dark. # Rain started falling soon after.",
    "45 # Bridge # River # The bridge connected two cities. # A river flowed beneath it.",
    "46 # Doctor # Medicine # The doctor prescribed medicine. # Medicine helps cure diseases.",
    "47 # Tree # Forest # The tree was tall. # The forest was dense with trees.",
    "48 # School # Learn # She went to school every day. # Learning is important for growth.",
    "49 # Farmer # Field # The farmer worked in the field. # The field was full of crops.",
    "50 # City # Traffic # The city was crowded. # Traffic was heavy during rush hour.",
    "51 # Knife # Sharp # His knife was very sharp. # Be careful with sharp objects.",
    "52 # Music # Dance # The music was loud. # They danced to the beat.",
    "53 # Mirror # Reflection # He looked into the mirror. # His reflection showed a tired face.",
    "54 # Police # Crime # The police caught the thief. # Crime was rising in the area.",
    "55 # Book # Page # She turned the page of her book. # The book was very interesting.",
    "56 # Rain # Flood # It rained heavily. # The flood covered the streets.",
    "57 # Wind # Storm # The wind was strong. # The storm was approaching fast.",
    "58 # Lamp # Light # He switched on the lamp. # The light filled the room.",
    "59 # Coffee # Mug # She poured coffee into her mug. # The mug was warm to touch.",
    "60 # Chef # Kitchen # The chef worked in the kitchen. # The kitchen smelled delicious.",
    "61 # Train # Travel # The train arrived on time. # Traveling by train is comfortable.",
    "62 # Medicine # Cure # The medicine helped him recover. # Cures for many diseases exist.",
    "63 # Newspaper # News # He read the newspaper daily. # The news was about politics.",
    "64 # Library # Quiet # The library was silent. # Quiet places help with studying.",
    "65 # Honey # Sweet # Honey is made by bees. # It tastes naturally sweet.",
    "66 # Plane # Fly # The plane took off. # It flew across the sky.",
    "67 # Actor # Movie # The actor was famous. # He starred in many movies.",
    "68 # Athlete # Run # The athlete ran fast. # Running is part of his training.",
    "69 # Traffic # Jam # The traffic was slow. # A traffic jam delayed everyone.",
    "70 # Salt # Ocean # The ocean water is salty. # Salt is extracted from seawater.",
    "71 # Key # Door # She used a key. # The door unlocked easily.",
    "72 # Earth # Planet # The Earth is our home. # It is the third planet from the sun.",
    "73 # Candle # Fire # The candle burned brightly. # Fire flickered at its tip.",
    "74 # Festival # Celebration # The festival was lively. # People celebrated together.",
    "75 # Artist # Paint # The artist created a masterpiece. # She used paint and brushes.",
]

system_prompt = """
You are an intelligent language assistant that helps users memorize vocabulary by finding meaningful connections between words in a given text and stored vocabulary words.
"""
prompt =  """
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

Now, Create output for this input. Do not attempt to process all inputs at once. Always complete an output before moving to the next input.
Input:

"""
import logging
logging.basicConfig(
    filename='log.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding="utf-8" 
)

import asyncio
import pprint
async def exe(prompt, model, model_idx):
   start = time.time()
   response = await freeLLM.send_prompt(prompt, model, system_prompt)
   print(f"model_idx: {model_idx}")
   print(f"model: {model}")
   print(f"Time taken for prompt: {time.time() - start}")
   
   #llm_response = response["choices"][0]["message"]["content"]
   pprint.pprint(response)


def split_into_chunks(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

async def main():
    
    lists_sub_inputs = split_into_chunks(inputs, 5)  # Split the inputs into chunks of size 1
    models = ["bytedance-research/ui-tars-72b:free", "mistralai/mistral-small-3.1-24b-instruct:free", "rekaai/reka-flash-3:free"]
    tasks= []
    model_idx=1
    for sub_inputs in lists_sub_inputs:
        llm_prompt = prompt + "\n".join(sub_inputs)
        tasks.append(exe(llm_prompt, models[model_idx % len(models)],model_idx))
        model_idx+=1
    start = time.time()
    await asyncio.gather(*tasks)
    print("Time taken:", time.time() - start)
  
if __name__ == "__main__":
    asyncio.run(main())