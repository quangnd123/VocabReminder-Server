import sys
if "F:\\VocabReminder\\backend" not in sys.path:
    sys.path.append("F:\\VocabReminder\\backend")

from llm.free import FreeLLM
import logging
import time 

freeLLM = FreeLLM()

prompt = f"""
## Task:
You're helping a language learner recall vocabulary by linking it with real-world usage they encounter while browsing.

**Input Format:**
<ID> # <word users see> # <vocab users want to memorize> # <word_context> # <vocab_context>

**Output Format:**
<ID> # <CONNECTION_TYPE> # <Concise, vivid mnemonic reminder in vietnamese that clearly connects the two words and their contexts. Include both words and refer to their original sentences.>

**Instructions:**
- For each line, find a strong and understandable link between the word the user saw and the vocabulary they’re trying to remember.
- Use semantic relationships such as: Synonym, Antonym, Hypernym, Hyponym, Meronym, Holonym, Causality, Troponym, Complementarity, Etymology, or Collocation.
- You may also use grammar links (e.g. same root), emotional cues, visual imagery, or shared phrases.
- Use the provided contexts to disambiguate meanings and inspire the mnemonic.
- If the vocabulary word the **user** wants to memorize has already appeared in the sentence seen, emphasize repeated exposure in a new context to reinforce memory.
- The mnemonic reminder should include:
  - Both the seen word and the vocab word (in their original form),
  - A vivid mental connection in vietnamese,
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

1 # The # rainbow # The sun rises in the east. # A rainbow appeared after the rain.
2 # sun # sun # The sun rises in the east. # The sun dipped below the mountain.
3 # in # quyển sách # The sun rises in the east. # Tôi đang đọc một quyển sách hay.
4 # She # tiếng Anh # She enjoys reading books at night. # Cô ấy đang học tiếng Anh mỗi ngày.
5 # reading # nghe nhạc # She enjoys reading books at night. # Tôi thích nghe nhạc mỗi khi rảnh.
6 # books # quyển sách # She enjoys reading books at night. # Tôi đang đọc một quyển sách hay.
7 # at # whispered a secret # She enjoys reading books at night. # He whispered a secret to his friend.
8 # night # nhà hàng Nhật # She enjoys reading books at night. # Chúng tôi ăn tối ở một nhà hàng Nhật.
9 # umbrella # rainbow # I forgot my umbrella at home. # A rainbow appeared after the rain.
10 # children # Trẻ con # The children are playing in the yard. # Trẻ con chơi đùa ngoài sân.
11 # playing # trồng cây # The children are playing in the yard. # Bố tôi thích trồng cây trong vườn.
12 # in # playing in the park # The children are playing in the yard. # Children were playing in the park.
13 # you # dọn dẹp # Can you help me with this task? # Chúng ta cần dọn dẹp phòng này.
14 # task # bài kiểm tra # Can you help me with this task? # Học sinh đang làm bài kiểm tra.
15 # coffee # cà phê # He always drinks coffee in the morning. # Tôi uống cà phê mỗi sáng.
16 # to # Đà Lạt # We are planning a trip to Da Nang. # Họ đi chơi ở Đà Lạt cuối tuần qua.
17 # excellent # bữa ăn ngon # This phone has excellent battery life. # Mẹ tôi nấu bữa ăn ngon.
18 # the # dọn dẹp # Don’t forget to lock the door. # Chúng ta cần dọn dẹp phòng này.
19 # sound # Music # I love the sound of rain. # Music filled the entire room with joy.
20 # rain # rainbow # I love the sound of rain. # A rainbow appeared after the rain.
21 # She # Cô giáo # She is learning how to cook Vietnamese food. # Cô giáo dạy học sinh rất tận tâm.
22 # learning # tiếng Anh # She is learning how to cook Vietnamese food. # Cô ấy đang học tiếng Anh mỗi ngày.
23 # cook # bài kiểm tra # She is learning how to cook Vietnamese food. # Học sinh đang làm bài kiểm tra.
24 # food # bữa ăn ngon # She is learning how to cook Vietnamese food. # Mẹ tôi nấu bữa ăn ngon.
25 # The # dọn dẹp # The teacher gave us a lot of homework. # Chúng ta cần dọn dẹp phòng này.
26 # teacher # telescope # The teacher gave us a lot of homework. # He studied the stars through his telescope.
27 # homework # bài kiểm tra # The teacher gave us a lot of homework. # Học sinh đang làm bài kiểm tra.
28 # My # bữa ăn ngon # My father watches the news every evening. # Mẹ tôi nấu bữa ăn ngon.
29 # watches # telescope # My father watches the news every evening. # He studied the stars through his telescope.
30 # the # phim truyền hình # My father watches the news every evening. # Bà tôi thích xem phim truyền hình.
31 # news # nghe nhạc # My father watches the news every evening. # Tôi thích nghe nhạc mỗi khi rảnh.
32 # a # Con mèo # There is a cat sleeping on the sofa. # Con mèo đang nằm ngủ trên ghế sofa.
33 # I # nghe nhạc # I usually go jogging in the park. # Tôi thích nghe nhạc mỗi khi rảnh.
34 # the # trồng cây # I usually go jogging in the park. # Bố tôi thích trồng cây trong vườn.
35 # park # playing in the park # I usually go jogging in the park. # Children were playing in the park.
36 # movie # phim truyền hình # This movie is very touching. # Bà tôi thích xem phim truyền hình.
37 # She # Cô giáo # She wore a beautiful red dress. # Cô giáo dạy học sinh rất tận tâm.
38 # beautiful # trong lành # She wore a beautiful red dress. # Trời hôm nay rất đẹp và trong lành.
39 # Mặt trời # storm # Mặt trời mọc ở hướng đông. # A storm was brewing on the horizon.
40 # đọc # nghe nhạc # Cô ấy thích đọc sách vào ban đêm. # Tôi thích nghe nhạc mỗi khi rảnh.
41 # sách # opened the book # Cô ấy thích đọc sách vào ban đêm. # He opened the book and started reading.
42 # trẻ # Trẻ con # Lũ trẻ đang chơi ngoài sân. # Trẻ con chơi đùa ngoài sân.
43 # chơi # playing in the park # Lũ trẻ đang chơi ngoài sân. # Children were playing in the park.
44 # sân # trồng cây # Lũ trẻ đang chơi ngoài sân. # Bố tôi thích trồng cây trong vườn.
45 # có thể # opened the book # Bạn có thể giúp tôi việc này không? # He opened the book and started reading.
46 # tôi # nghe nhạc # Bạn có thể giúp tôi việc này không? # Tôi thích nghe nhạc mỗi khi rảnh.
47 # việc # dọn dẹp # Bạn có thể giúp tôi việc này không? # Chúng ta cần dọn dẹp phòng này.
48 # cà phê # hot coffee # Anh ấy luôn uống cà phê vào buổi sáng. # He poured a cup of hot coffee.
49 # Đà Nẵng # Đà Lạt # Chúng tôi đang lên kế hoạch đi Đà Nẵng. # Họ đi chơi ở Đà Lạt cuối tuần qua.


"""



