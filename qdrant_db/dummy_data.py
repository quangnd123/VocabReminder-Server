original_words =[

    ("en", "He had to shout over the noise to be heard.", "shout"),
    ("en", "They plan to build a new library downtown.", "build"),
    ("en", "She opened the window to let in fresh air.", "opened"),
    ("en", "He likes to run in the mornings before work.", "run"),
    ("en", "The room was bright and cheerful.", "bright")

]

sample_data = [
#shout
{
    "synonym": ("en", "She yelled at the top of her lungs.", "yelled"),
    "antonym": ("en", "He whispered softly into her ear.", "whispered"),
    "hypernym": ("en", "The coach made a sound to get attention.", "sound"),
    "hyponym": ("en", "The protester screamed with anger.", "screamed"),
    "meronym": ("en", "His voice cracked during the loud shout.", "voice"),
    "holonym": ("en", "A shout was part of his emotional outburst.", "outburst"),
    "causality": ("en", "He shouted because the alarm startled him.", "alarm"),
    "troponym": ("en", "He bellowed like a furious lion.", "bellowed"),
    "complementarity": ("en", "You either shout or stay silent.", "silent"),
    "etymological": ("en", "The word 'shout' has roots in Old English 'scēotan'.", "scēotan"),
    "collocation": ("en", "He let out a sudden shout of joy.", "joy")
},

#build
{
    "synonym": ("en", "They will construct the school next year.", "construct"),
    "antonym": ("en", "They decided to demolish the old bridge.", "demolish"),
    "hypernym": ("en", "The team worked on the project all summer.", "project"),
    "hyponym": ("en", "He assembled the bookshelf in an hour.", "assembled"),
    "meronym": ("en", "They used bricks to build the wall.", "bricks"),
    "holonym": ("en", "The building includes a library and a gym.", "building"),
    "causality": ("en", "The growing population led them to build more homes.", "population"),
    "troponym": ("en", "She crafted a model house for the exhibition.", "crafted"),
    "complementarity": ("en", "You either build it or let it fall apart.", "fall"),
    "etymological": ("en", "‘Build’ is derived from Old Norse ‘byggja’.", "byggja"),
    "collocation": ("en", "They build strong relationships through trust.", "relationships")
},

#open
{
    "synonym": ("en", "He unlocked the door carefully.", "unlocked"),
    "antonym": ("en", "She closed the book and sighed.", "closed"),
    "hypernym": ("en", "He manipulated the object with care.", "manipulated"),
    "hyponym": ("en", "He unzipped his jacket as he entered.", "unzipped"),
    "meronym": ("en", "The handle creaked as she opened the door.", "handle"),
    "holonym": ("en", "The opening marked the start of the ceremony.", "opening"),
    "causality": ("en", "The heat made her open the window.", "heat"),
    "troponym": ("en", "She pushed the gate gently.", "pushed"),
    "complementarity": ("en", "To open it, it must not be closed.", "closed"),
    "etymological": ("en", "‘Open’ stems from Old English ‘openian’.", "openian"),
    "collocation": ("en", "He opened a bank account last week.", "account")
},

#run
{
    "synonym": ("en", "She jogs every evening at the park.", "jogs"),
    "antonym": ("en", "He stopped suddenly to catch his breath.", "stopped"),
    "hypernym": ("en", "They engage in exercise regularly.", "exercise"),
    "hyponym": ("en", "He sprinted the last 100 meters.", "sprinted"),
    "meronym": ("en", "His legs moved fast as he ran downhill.", "legs"),
    "holonym": ("en", "Running is part of his morning routine.", "routine"),
    "causality": ("en", "He runs to stay healthy.", "healthy"),
    "troponym": ("en", "He dashed across the street.", "dashed"),
    "complementarity": ("en", "You either run or stay still.", "still"),
    "etymological": ("en", "‘Run’ comes from Old English ‘rinnan’.", "rinnan"),
    "collocation": ("en", "He runs a marathon every year.", "marathon")
},

#bright
{
    "synonym": ("en", "The hallway was luminous with sunlight.", "luminous"),
    "antonym": ("en", "The basement was dark and cold.", "dark"),
    "hypernym": ("en", "She preferred vivid colors in her home.", "vivid"),
    "hyponym": ("en", "The neon sign was glaring in the night.", "glaring"),
    "meronym": ("en", "The bright color of the lamp lit up the room.", "color"),
    "holonym": ("en", "The brightness of the room made her smile.", "brightness"),
    "causality": ("en", "The clean windows made the room appear bright.", "windows"),
    "troponym": ("en", "The glossy finish made the wall look bright.", "glossy"),
    "complementarity": ("en", "The sky is either bright or gloomy.", "gloomy"),
    "etymological": ("en", "‘Bright’ traces back to Old English ‘beorht’.", "beorht"),
    "collocation": ("en", "She wore a bright smile all day.", "smile")
}


]


neg_examples = [
    ("en", "He poured orange juice into the glass.", "juice"),
    ("en", "The mountain is covered with snow.", "mountain"),
    ("en", "She painted a landscape of the desert.", "desert"),
    ("en", "The dog chased the cat across the yard.", "cat"),
    ("en", "He used a hammer to fix the chair.", "hammer"),
    ("en", "The music was too loud for her liking.", "music"),
    ("en", "She bought a necklace from the market.", "necklace"),
    ("en", "They played football on Saturday.", "football"),
    ("en", "The sun set behind the tall buildings.", "sun"),
    ("en", "He wrote his name on the whiteboard.", "whiteboard"),
    ("en", "The child opened the gift eagerly.", "gift"),
    ("en", "She folded the laundry neatly.", "laundry"),
    ("en", "The car engine started with a roar.", "engine"),
    ("en", "He looked through the telescope.", "telescope"),
    ("en", "They climbed the stairs slowly.", "stairs"),
    ("en", "The balloon floated into the sky.", "balloon"),
    ("en", "She arranged the books alphabetically.", "books"),
    ("en", "He swam across the river quickly.", "river"),
    ("en", "The candle burned brightly.", "candle"),
    ("en", "The teacher graded the papers.", "graded"),
    ("en", "She added honey to her tea.", "honey"),
    ("en", "They built a campfire in the woods.", "campfire"),
    ("en", "The baby crawled across the floor.", "baby"),
    ("en", "He sneezed loudly in the classroom.", "sneezed"),
    ("en", "The airplane flew above the clouds.", "airplane"),
    ("en", "She typed the letter carefully.", "typed"),
    ("en", "They installed a new doorbell.", "doorbell"),
    ("en", "The chef sliced the vegetables.", "chef"),
    ("en", "He painted the fence white.", "fence"),
    ("en", "The wind howled through the trees.", "wind"),
    ("en", "She measured the fabric twice.", "fabric"),
    ("en", "The rabbit hopped away quickly.", "rabbit"),
    ("en", "He watered the plants every day.", "plants"),
    ("en", "The bell rang at noon.", "bell"),
    ("en", "She whispered a secret to her friend.", "secret"),
    ("en", "The clock ticked loudly in the silence.", "clock"),
    ("en", "He sketched a portrait of his sister.", "portrait"),
    ("en", "They admired the sunset at the beach.", "sunset"),
    ("en", "She picked fresh strawberries from the garden.", "strawberries"),
    ("en", "The train arrived ten minutes late.", "train"),
    ("en", "He adjusted the mirror before driving.", "mirror"),
    ("en", "The kitten slept in a warm blanket.", "kitten"),
    ("en", "She filed the documents carefully.", "documents"),
    ("en", "He glued the pieces together.", "glued"),
    ("en", "The spider built a web in the corner.", "spider"),
    ("en", "They packed their bags for the trip.", "bags"),
    ("en", "She wore a red scarf.", "scarf"),
    ("en", "The leaves rustled in the breeze.", "leaves"),
    ("en", "He opened the umbrella as it started to rain.", "umbrella")
]
