import torch
import torch.nn.functional as F
from transformers import PreTrainedModel, PreTrainedTokenizer
from abc import ABC, abstractmethod
from typing import List
import re 
from logger.logger import get_logger

logger = get_logger(__name__, "embedding.log")

class BaseEmbedder(ABC):
    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        """
        Initializes the embedding model and tokenizer.

        Args:
            model (PreTrainedModel): The pre-trained model for embeddings.
            tokenizer (PreTrainedTokenizer): The tokenizer corresponding to the model.
        """
        self.tokenizer = tokenizer
        self.model = model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.ignore_pos = [] 

    def tokenize_into_tokens(self, sentences: list[str], add_special_tokens: bool=False) -> list[list[str]]:
        """
        Tokenizes sentences into tokens.

        Args:
            sentences (list[str]): a list of sentence.

        Returns:
            list[list[str]]: (num_sentences, num_tokens) each element is a string.
        """

        encoded = self.tokenizer(
            sentences,
            add_special_tokens=add_special_tokens,
            return_attention_mask=False,
            return_token_type_ids=False,
            padding=False,
            truncation=False,
        )
        return [self.tokenizer.convert_ids_to_tokens(ids) for ids in encoded["input_ids"]]

    @abstractmethod
    def tokenize_into_words(self, sentences: list[str]) -> list[list[dict]]:
        """
        Splits sentences into words.

        Args:
            sentences (list[str]): a list of sentence.

        Returns:
            list[list[dict]]: (num_sentences, num_words) each element is a word data dictionary of keys {"word", "pos"}.
        """
        pass
    
    def get_word_indices(self, sentence: str, words: list[str]) -> list[int]:
        """
        Gets the indices for all words in a sentence.

        Args:
            sentence (str): The input sentence.

        Returns:
            List[int]: A list of words' indices.
        """
        idx = 0
        word_indices = []
        for word in words:
            word_idx = sentence.find(word, idx)
            word_indices.append(word_idx)
            idx = word_idx + len(word)
        return word_indices

    def get_token_embedding(self, sentences: list[str]) -> list[list[torch.Tensor]]:
        """
        Generates token-level embeddings for a list of sentences.

        Args:
            sentences (list[str]): A list of sentences.

        Returns:
            list[list[torch.Tensor]]: (num_sentences, num_tokens) each element is a vector of size hidden_dim
        """
        inputs = self.tokenizer(
            sentences, return_tensors="pt", padding=True, truncation=True, add_special_tokens=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        embeddings = outputs.last_hidden_state  # Shape: (num_sentences, max_num_tokens, hidden_dim)
        attention_mask = inputs["attention_mask"]  # Shape: (num_sentences, max_num_tokens)

        # Remove padding tokens
        return [embeddings[i, :int(attention_mask[i].sum().item())] for i in range(len(sentences))] #(num_sentences, num_tokens, hidden_dim)

    def align_words_with_tokens(self, sentence: str, word_data_1d: list[dict], tokens: list[str]) -> List[dict]:
        """
        Example: sentence = "haven't", words = ["have", "n't"], tokens = ["haven", "'", "t"]
        We can't get embeddings for these words. So, the only choice is to have only one word "haven't" with embedding as the average of the tokens' embeddings
        Args:
            sentence (str): The input sentence.
            word_data_1d (list[dict]): a list of data for words in sentence with keys {"word", "pos"}.
            tokens list[str]: a list of tokens in sentence

        Returns:
            List[dict]: A list of word data dictionary with keys {"word", "token", "token_range", "word_idx", "ignore"}.
        """

        # Remove '▁'(word boundary of tokenization models, not underscore) and whitespace(spaces, tabs, newlines)
        no_space_tokens = [re.sub(r"[▁\s]+", "", token) for token in tokens]
        no_space_words = [re.sub(r"[▁\s]+", "", word_data["word"]) for word_data in word_data_1d]

        start_token_idx = 1 # Skip the first token (CLS token)
        end_token_idx = start_token_idx + 1

        start_word_idx = 0
        end_word_idx = start_word_idx + 1
        
        new_words_data = [] 

        while(start_token_idx < len(tokens)-1 and start_word_idx < len(word_data_1d)):
            current_word = no_space_words[start_word_idx]
            current_token = no_space_tokens[start_token_idx]
            
            while(len(current_word) != len(current_token)):
                if(len(current_word) > len(current_token)):
                    next_token = no_space_tokens[end_token_idx]
                    current_token = current_token + next_token
                    end_token_idx += 1
                else:
                    next_word = no_space_words[end_word_idx]
                    current_word = current_word + next_word
                    end_word_idx += 1
            
            if current_word != current_token:
                logger.error(f"Sentence: {sentence}")
                logger.error(f"Word and token mismatch: {current_word} != {current_token}")

            token =""
            for i in range(start_token_idx, end_token_idx):
                token += tokens[i]
            word = token.replace("▁", " ").strip()

            new_words_data.append(
                {
                    "word": word, 
                    "token": token,
                    "ignore": all(word_data_1d[i]["pos"] in self.ignore_pos for i in range(start_word_idx, end_word_idx)), 
                    "token_range": (start_token_idx, end_token_idx)
                }
            )

            start_token_idx = end_token_idx
            start_word_idx = end_word_idx

            end_token_idx += 1
            end_word_idx += 1

        # find sentence-based index for each word
        words = [word_data["word"] for word_data in new_words_data]
        word_indices = self.get_word_indices(sentence=sentence, words=words)
        for word_data, word_idx in zip(new_words_data, word_indices):
            word_data["word_idx"] = word_idx
        
        return new_words_data

    def get_word_embedding(self, sentences: list[str], token_2d: list[list[str]], token_embedding_2d: list[list[torch.Tensor]]) -> list[list[torch.Tensor]]:
        """
        Generates word-level embeddings for a list of sentences.

        Args:
            sentences (list[str]): A list of sentences.
            token_embedding_2d (list[list[torch.Tensor]]): (num_sentences, num_tokens), each element is a token vector of size hidden_dim
        Returns:
            list[list[torch.Tensor]] : (num_sentences, num_words), each element is a word vector of size hidden_dim
        """
        word_data_2d = self.tokenize_into_words(sentences=sentences)
        
        word_embedding_2d=[] #(num_sentences, num_words, hidden_dim)
        new_word_data_2d=[]
        for sentence, word_data_1d, token_1d, token_embedding_1d in zip(sentences, word_data_2d, token_2d, token_embedding_2d):
            new_word_data_1d = self.align_words_with_tokens(sentence=sentence, word_data_1d=word_data_1d, tokens=token_1d)
            new_word_data_2d.append(new_word_data_1d)

            word_embedding_1d = [] #(num_words, hidden_dim)
            for word_data in new_word_data_1d:
                word_embedding = token_embedding_1d[word_data["token_range"][0]:word_data["token_range"][1]].mean(dim=0)
                word_embedding_1d.append(word_embedding)
            word_embedding_2d.append(word_embedding_1d)
        
        return new_word_data_2d, word_embedding_2d
            
    def get_phrase_embedding(self, sentence: str, phrase: str, phrase_idx: int) -> torch.Tensor:
        """
        Extracts an embedding for a specific phrase within a sentence.

        Args:
            sentence (str): The input sentence.
            phrase (str): The target phrase.
            phrase_idx (int): The starting index of the phrase in the sentence
            
        Returns:
            torch.Tensor: The embedding of the phrase.
        """

        token_1d = self.tokenize_into_tokens(sentences=[sentence], add_special_tokens=True)[0]
        token_embedding_1d = self.get_token_embedding(sentences=[sentence])[0]

        word_data_1d = self.tokenize_into_words(sentences=[sentence])[0]
        word_data_1d = self.align_words_with_tokens(sentence=sentence, word_data_1d=word_data_1d, tokens=token_1d)
        
        word_embedding_1d = []
        for word_data in word_data_1d:
            word_embedding = token_embedding_1d[word_data["token_range"][0]:word_data["token_range"][1]].mean(dim=0)
            word_embedding_1d.append(word_embedding)

        start = -1
        for i in range(len(word_data_1d)):
            if phrase_idx >= word_data_1d[i]["word_idx"]:
                start = i
            else:
                break
        
        end = start+1
        phrase_end_idx = phrase_idx + len(phrase)
        for i in range(start+1, len(word_data_1d)):
            if phrase_end_idx > word_data_1d[i]["word_idx"]:
                end = i+1
            else:
                break

        if start == -1 or end ==-1:
            logger.error(f"Phrase {phrase} with idx {phrase_idx} not found in the sentence: {sentence}")
            raise Exception(f"Phrase {phrase} with idx {phrase_idx} not found in the sentence: {sentence}")
        
        phrase_embedding = torch.stack(word_embedding_1d[start:end]).mean(dim=0) # (hidden_dim)
        new_phrase_idx = word_data_1d[start]["word_idx"]
        token = ""
        for i in range (start, end):
            token += word_data_1d[i]["token"]
        new_phrase = token.replace("▁", " ").strip()

        return new_phrase, new_phrase_idx, phrase_embedding 
    
    def get_cossim_phrases(self, phrase_1, phrase_idx_1, sentence_1, phrase_2, phrase_idx_2, sentence_2):
        _, _, emb_1 = self.get_phrase_embedding(phrase=phrase_1, phrase_idx=phrase_idx_1, sentence=sentence_1)
        _, _, emb_2 = self.get_phrase_embedding(phrase=phrase_2, phrase_idx=phrase_idx_2, sentence=sentence_2)
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))
    
    def get_cossim_sentences(self, sentence_1, sentence_2):
        emb_1 = self.get_token_embedding(sentence=sentence_1)[0][0]
        emb_2 = self.get_token_embedding(sentence=sentence_2)[0][0]
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))