word_sentence_pairs = [
    # Semantic theme for the sentence:
    {
        "word": "damage",
        "sentence": "The heavy rain resulted in significant damage throughout the old building."
    },
    #
    # For "roof" group (sentences avoid the word 'roof'):
    {
        "word": "covering",
        "sentence": "The shelter's covering withstood the fierce storm without a tear."
    },
    {
        "word": "basement",
        "sentence": "After the downpour, water began seeping into the basement of the cottage."
    },
    {
        "word": "structure",
        "sentence": "The ancient structure showed signs of wear from years of exposure to the elements."
    },
    {
        "word": "shingle",
        "sentence": "A single shingle was dislodged by the violent gusts during the tempest."
    },
    {
        "word": "tile",
        "sentence": "The ceramic tile on the upper level added a touch of elegance to the building."
    },
    {
        "word": "house",
        "sentence": "The charming house stood firm even as the storm battered its exterior."
    },
    {
        "word": "collapse",
        "sentence": "Years of neglect and moisture eventually led to a sudden collapse of the upper structure."
    },
    {
        "word": "deteriorate",
        "sentence": "Without proper maintenance, the materials began to deteriorate rapidly under harsh weather."
    },
    {
        "word": "foundation",
        "sentence": "Cracks appeared in the foundation after the relentless pounding of the rain."
    },
    {
        "word": "roofness",
        "sentence": "Her sketches captured an abstract sense of roofness that defied conventional design."
    },
    #
    # For "leaking" group:
    {
        "word": "leak",
        "sentence": "A small leak in the plumbing went unnoticed until water stained the floor."
    },
    {
        "word": "dripping",
        "sentence": "The constant dripping from the old pipe echoed through the silent hallway."
    },
    {
        "word": "sealed",
        "sentence": "All the joints were carefully sealed to ensure no moisture could enter."
    },
    {
        "word": "discharge",
        "sentence": "The drainage system is designed to discharge excess water during heavy rains."
    },
    {
        "word": "seepage",
        "sentence": "Slow seepage along the wall eventually raised concerns among the engineers."
    },
    {
        "word": "trickle",
        "sentence": "A gentle trickle of water ran down the window, marking the start of the storm."
    },
    {
        "word": "repair",
        "sentence": "They called a specialist to repair the worn-out pipe before any major issues occurred."
    },
    {
        "word": "leakage",
        "sentence": "Persistent leakage over time weakened the insulation of the old structure."
    },
    #
    # For "rain" group:
    {
        "word": "downpour",
        "sentence": "A sudden downpour drenched the city streets in less than a minute."
    },
    {
        "word": "drought,",
        "sentence": "After a long drought, even a small amount of rain was eagerly welcomed."
    },
    {
        "word": "precipitation",
        "sentence": "Meteorologists predicted that unusual precipitation would continue throughout the week."
    },
    {
        "word": "drizzle",
        "sentence": "A light drizzle in the early morning set a calm and peaceful tone for the day."
    },
    {
        "word": "raindrop",
        "sentence": "A solitary raindrop clung to a leaf before joining a larger pool of water."
    },
    {
        "word": "storm",
        "sentence": "The approaching storm darkened the sky and stirred the winds into a frenzy."
    },
    {
        "word": "flood",
        "sentence": "Intense rainfall led to a flood that temporarily disrupted local traffic."
    },
    {
        "word": "shower",
        "sentence": "A brief shower passed over the town, leaving behind a refreshed landscape."
    },
    {
        "word": "umbrella",
        "sentence": "She opened her umbrella just in time to dodge the sudden rain."
    },
    {
        "word": "regn",
        "sentence": "Ancient legends spoke of a time when relentless regn flooded the lands for days."
    },
    #
    # For "heavy" group:
    {
        "word": "weighty",
        "sentence": "The weighty decision was not made lightly by the council."
    },
    {
        "word": "light",
        "sentence": "The artist contrasted the light fabrics with dark, somber tones in the exhibit."
    },
    {
        "word": "intense",
        "sentence": "The intense atmosphere in the room left everyone feeling both exhilarated and nervous."
    },
    {
        "word": "massive",
        "sentence": "A massive sculpture dominated the plaza, drawing the attention of passersby."
    },
    {
        "word": "pound",
        "sentence": "Rain began to pound against the windows with a relentless rhythm."
    },
    {
        "word": "load",
        "sentence": "The bridge was engineered to carry a heavy load without compromising safety."
    },
    {
        "word": "overburden",
        "sentence": "Years of neglect caused the aging structure to overburden under constant pressure."
    },
    {
        "word": "weigh",
        "sentence": "The responsibility seemed to weigh on his shoulders as he faced the challenges ahead."
    },
    {
        "word": "lightness",
        "sentence": "Her voice conveyed a rare lightness that brightened even the dullest moments."
    },
    {
        "word": "heaviness",
        "sentence": "The heaviness of the situation was palpable as the verdict was delivered."
    },
    #
    # Extra small words (articles, auxiliary verbs, etc.)
    {
        "word": "the",
        "sentence": "The word 'the' is the most frequently used definite article in English."
    },
    {
        "word": "a",
        "sentence": "a is an indefinite article used before singular, countable nouns."
    },
    # {
    #     "word": "an",
    #     "sentence": "an is an indefinite article that precedes words beginning with a vowel sound."
    # },
    {
        "word": "roof",
        "sentence": "The roof provided essential shelter during the torrential downpour."
    },
    # {
    #     "word": "was",
    #     "sentence": "'Was' is the past tense form of the verb 'to be' in English."
    # },
    # {
    #     "word": "be",
    #     "sentence": "The verb 'be' is fundamental in constructing English sentences."
    # },
    # {
    #     "word": "is",
    #     "sentence": "'Is' serves as the present tense of the verb 'to be' for singular subjects."
    # },
    # {
    #     "word": "are",
    #     "sentence": "'Are' is used as the present tense of the verb 'to be' for plural subjects."
    # },
    # {
    #     "word": "were",
    #     "sentence": "'Were' is the past tense form used with plural subjects or with 'you.'"
    # },
    {
        "word": "leaking,",
        "sentence": "The old pipes were leaking, prompting a call for urgent repairs."
    },
    {
        "word": "after",
        "sentence": "after the rain, the streets shone under the city lights."
    },
    {
        "word": "before",
        "sentence": "before the storm hit, the sky was an eerie shade of gray."
    },
    # {
    #     "word": "in front of",
    #     "sentence": "He parked his car in front of the building to admire its architecture."
    # },
    {
        "word": "besides",
        "sentence": "besides the constant rain, the weather remained surprisingly calm."
    },
    {
        "word": "heavy",
        "sentence": "Dark, heavy clouds loomed on the horizon as the storm approached."
    },
    {
        "word": "rain",
        "sentence": "rain transformed the barren landscape into a scene bursting with life."
    },
    {
        "word": "bright",
        "sentence": "She is a bright student."
    },
    {
        "word": "bright",
        "sentence": "The sun is very bright today."
    },
    {
        "word": "smart",
        "sentence": "She is a smart student who learns quickly."
    },
    {
        "word": "dull",
        "sentence": "She is a dull student who struggles to understand concepts."
    },
    {
        "word": "luminous",
        "sentence": "The sun is so luminous that I need sunglasses."
    },
        {
        "word": "dark",
        "sentence": "The room was so dark that I could barely see."
    },
    {
        "word": "reversal",
        "sentence": "She had a reversal in her decision and chose to forgive him."
    },
    {
        "word": "changed",
        "sentence": "I changed my outfit."
    },
]

w = "bright"
s = "a bright person is an intelligent and quick-witted person."

target_word = "光"  # Light
target_sentence = "光是宇宙中的一种能量形式。"  # Light is a form of energy in the universe.

# Define related words with their relations and example sentences
related_words = {
    "Synonym": ("亮光", "亮光照亮了整个房间。"),  # Bright light → The bright light illuminated the entire room.
    "Antonym": ("黑暗", "黑暗笼罩着森林。"),  # Darkness → Darkness shrouded the forest.
    "Hypernym": ("能量", "能量以多种形式存在，例如光和热。"),  # Energy → Energy exists in various forms, such as light and heat.
    "Hyponym": ("阳光", "阳光透过窗户洒在地板上。"),  # Sunlight → Sunlight shone through the window onto the floor.
    "Meronym": ("光子", "光子是光的基本组成部分。"),  # Photon → Photons are the fundamental components of light.
    "Holonym": ("宇宙", "整个宇宙充满了光和尘埃。"),  # Universe → The entire universe is filled with light and dust.
    "Causality": ("太阳", "太阳的光使植物生长。"),  # Sun → The sun’s light enables plants to grow.
    "Troponym": ("霓虹灯", "霓虹灯在夜晚闪耀。"),  # Neon light → The neon light shines at night.
    "Complementarity": ("影子", "影子是由光产生的。"),  # Shadow → Shadows are created by light.
    "Etymological": ("光明", "光明意味着希望和未来。")  # Brightness → Brightness symbolizes hope and the future.
}


word_relations = {
    "Synonym": {
        "target": {"word": "happy", "context": "She felt truly happy when she reunited with her childhood friend after years."},
        "positive": [
            {"word": "joyful.", "context": "The children's laughter made the room feel joyful."},
            {"word": "cheerful", "context": "Despite the rain, he remained cheerful throughout the trip."},
            {"word": "glad", "context": "I'm glad you could make it to the event."}
        ],
        "negative": [
            {"word": "sad", "context": "He looked sad after hearing the disappointing news."},
            {"word": "angry", "context": "She was angry when she realized her wallet was missing."},
            {"word": "dark", "context": "The story took a dark turn in the final chapter."}
        ]
    },
    "Antonym": {
        "target": {"word": "hot", "context": "The coffee was too hot to drink immediately."},
        "positive": [
            {"word": "cold.", "context": "The winter night was unbearably cold."},
            {"word": "freezing", "context": "His hands were freezing after spending hours outside."},
            {"word": "chilly", "context": "She put on a jacket because it was a bit chilly outside."}
        ],
        "negative": [
            {"word": "warm", "context": "The blanket kept her warm during the storm."},
            {"word": "boiling", "context": "The soup was boiling on the stove."},
            {"word": "summer.", "context": "They planned a vacation for the summer."}
        ]
    },
    "Hypernym": {
        "target": {"word": "dog", "context": "Her dog wagged its tail excitedly when she came home."},
        "positive": [
            {"word": "animals.", "context": "The zoo had a wide variety of animals."},
            {"word": "mammal", "context": "A whale is the largest mammal in the ocean."},
            {"word": "pet", "context": "She adopted a pet from the animal shelter."}
        ],
        "negative": [
            {"word": "table.", "context": "He placed his coffee cup on the table."},
            {"word": "chair", "context": "She pulled out a chair and sat down."},
            {"word": "phone", "context": "He answered his phone quickly."}
        ]
    },
    "Hyponym": {
        "target": {"word": "vehicle", "context": "A vehicle is essential for long-distance travel."},
        "positive": [
            {"word": "car", "context": "He parked his car in the driveway."},
            {"word": "bicycle", "context": "She enjoys riding her bicycle in the park."},
            {"word": "motorcycle", "context": "His motorcycle roared down the highway."}
        ],
        "negative": [
            {"word": "tree", "context": "The tree provided shade on a hot day."},
            {"word": "book.", "context": "She spent the afternoon reading a book."},
            {"word": "orange", "context": "He peeled an orange for a snack."}
        ]
    },
    "Meronym": {
        "target": {"word": "tree", "context": "The tree swayed gently in the wind."},
        "positive": [
            {"word": "leaf", "context": "A single leaf drifted to the ground."},
            {"word": "branch.", "context": "The cat climbed up the branch."},
            {"word": "bark", "context": "The bark of the tree was rough to the touch."}
        ],
        "negative": [
            {"word": "river", "context": "The river flowed rapidly after the storm."},
            {"word": "sky", "context": "The sky was clear and blue."},
            {"word": "house", "context": "Their house was located on a quiet street."}
        ]
    }
}


word_relations_vi = {
    "Từ đồng nghĩa": {
        "target": {"word": "hạnh phúc", "context": "Cô ấy cảm thấy thực sự hạnh phúc khi đoàn tụ với bạn thời thơ ấu sau nhiều năm."},
        "positive": [
            {"word": "vui vẻ", "context": "Tiếng cười của trẻ con khiến căn phòng trở nên vui vẻ."},
            {"word": "phấn chấn", "context": "Mặc dù trời mưa, anh ấy vẫn phấn chấn suốt chuyến đi."},
            {"word": "mừng", "context": "Tôi mừng vì bạn đã đến sự kiện."}
        ],
        "negative": [
            {"word": "buồn", "context": "Anh ấy trông buồn sau khi nghe tin không vui."},
            {"word": "giận", "context": "Cô ấy rất giận khi nhận ra ví tiền mình bị mất."},
            {"word": "tối tăm", "context": "Câu chuyện trở nên tối tăm trong chương cuối."}
        ]
    },
    "Từ trái nghĩa": {
        "target": {"word": "nóng", "context": "Cà phê quá nóng để uống ngay."},
        "positive": [
            {"word": "lạnh", "context": "Đêm đông lạnh giá không chịu nổi."},
            {"word": "đóng băng", "context": "Tay anh ấy đóng băng sau nhiều giờ ở ngoài trời."},
            {"word": "se lạnh", "context": "Cô ấy khoác áo vì trời có chút se lạnh."}
        ],
        "negative": [
            {"word": "ấm áp", "context": "Chiếc chăn giữ cô ấy ấm áp trong cơn bão."},
            {"word": "sôi sùng sục", "context": "Nồi súp đang sôi sùng sục trên bếp."},
            {"word": "mùa hè", "context": "Họ dự định đi du lịch vào mùa hè."}
        ]
    },
    "Từ bao hàm": {
        "target": {"word": "chó", "context": "Chú chó vẫy đuôi vui mừng khi cô ấy về nhà."},
        "positive": [
            {"word": "động vật", "context": "Sân vườn bách thú có nhiều loài động vật khác nhau."},
            {"word": "động vật có vú", "context": "Cá voi là động vật có vú lớn nhất đại dương."},
            {"word": "thú cưng", "context": "Cô ấy đã nhận nuôi một chú thú cưng từ trại cứu hộ."}
        ],
        "negative": [
            {"word": "bàn", "context": "Anh đặt cái cốc lên bàn."},
            {"word": "ghế", "context": "Cô kéo ghế và ngồi xuống."},
            {"word": "điện thoại", "context": "Anh nhanh chóng trả lời điện thoại."}
        ]
    },
    "Từ bị bao hàm": {
        "target": {"word": "Phương tiện giao thông", "context": "Phương tiện giao thông rất cần thiết cho những chuyến đi dài."},
        "positive": [
            {"word": "xe hơi", "context": "Anh ấy đỗ xe hơi trong sân nhà."},
            {"word": "xe đạp", "context": "Cô ấy thích đạp xe đạp trong công viên."},
            {"word": "xe máy", "context": "Chiếc xe máy của anh ấy gầm rú trên đường cao tốc."}
        ],
        "negative": [
            {"word": "Cây", "context": "Cây xanh tạo bóng mát trong ngày hè nóng bức."},
            {"word": "sách", "context": "Cô ấy dành cả buổi chiều để đọc sách."},
            {"word": "cam", "context": "Anh ấy bóc một quả cam để ăn nhẹ."}
        ]
    },
    "Từ bộ phận": {
        "target": {"word": "Cây", "context": "Cây đung đưa nhẹ nhàng trong gió."},
        "positive": [
            {"word": "lá", "context": "Một chiếc lá rơi xuống mặt đất."},
            {"word": "cành", "context": "Con mèo trèo lên cành cây."},
            {"word": "Vỏ cây", "context": "Vỏ cây sần sùi khi chạm vào."}
        ],
        "negative": [
            {"word": "sông", "context": "Dòng sông chảy xiết sau cơn bão."},
            {"word": "Bầu trời", "context": "Bầu trời trong xanh và không một gợn mây."},
            {"word": "Ngôi nhà", "context": "Ngôi nhà của họ nằm trên một con phố yên tĩnh."}
        ]
    }
}
