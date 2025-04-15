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

    @abstractmethod
    def tokenize_into_words(self, text: str) -> List[dict]:
        """
        Splits a text into a list of words.

        Args:
            text (str): The input text.

        Returns:
            List[dict]: A list of words_data.
        """
        pass

    def get_word_data_1d(self, sentence: str) -> List[dict]:
        """
        Gets the words for a text.

        Args:
            text (str): The input text.

        Returns:
            List[dict]: A list of word data.
        """
        word_data_1d = self.tokenize_into_words(text=sentence)
        tokens = self.tokenize_into_tokens(text=sentence, add_special_tokens=True)

        # Remove '▁' and whitespace(spaces, tabs, newlines)
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
        word_indices = self.get_word_indices(text=sentence, words=words)
        for word_data, word_idx in zip(new_words_data, word_indices):
            word_data["word_idx"] = word_idx
        
        return new_words_data
    
    def get_word_data_2d(self, sentences: List[str]):
        word_data_2d = []
        for sentence in sentences:
            word_data_2d.append(self.get_word_data_1d(sentence=sentence))
        return word_data_2d

    def tokenize_into_tokens(self, text: str, add_special_tokens: bool = False) -> List[str]:
        """
        Tokenizes a text into subword tokens.

        Args:
            text (str): The input text.

        Returns:
            List[str]: A list of subword tokens.
        """
        return self.tokenizer.tokenize(text=text, add_special_tokens=add_special_tokens)

    def get_num_tokens(self, text: str) -> int:
        """
        Gets the number of tokens in a text.

        Args:
            text (str): The input text.

        Returns:
            int: The number of tokens in the text.
        """
        return len(self.tokenize_into_tokens(text=text))
    
    def get_word_indices(self, text: str, words: List[str]) -> List[int]:
        """
        Gets the indices for all words in a text.

        Args:
            text (str): The input text.

        Returns:
            List[int]: A list of words' indices.
        """
        idx = 0
        word_indices = []
        for word in words:
            word_idx = text.find(word, idx)
            word_indices.append(word_idx)
            idx = word_idx + len(word)
        return word_indices

    def get_token_embedding_1d(self, sentence: str) -> torch.Tensor:
        """
        Generates token-level embeddings for a sentence.

        Args:
            sentence (str): The input sentence.

        Returns:
            torch.Tensor: Token embeddings with shape (num_tokens, hidden_dim).
        """
        inputs = self.tokenizer(
            sentence, return_tensors="pt", padding=True, truncation=True, add_special_tokens=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        return outputs.last_hidden_state[0]  # Shape: (num_tokens, hidden_dim)

    def get_token_embedding_2d(self, sentences: List[str]) -> List[torch.Tensor]:
        """
        Generates token-level embeddings for a list of sentences.

        Args:
            sentences (List[str]): A list of sentences.

        Returns:
            List[torch.Tensor]: List of token embeddings per sentence.
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

    def get_word_embedding_1d(self, sentence: str, word_data_1d: List[dict]=None, token_embedding_1d = None) -> List[torch.Tensor]:
        """
        Generates word-level embeddings for a sentence.

        Args:
            sentence (str): The input sentence.

        Returns:
            List[torch.Tensor]:  Word embeddings (num_words, hidden_dim)
        """
        if word_data_1d is None:
            word_data_1d = self.get_word_data_1d(sentence=sentence)

        if token_embedding_1d is None:
            token_embedding_1d = self.get_token_embedding_1d(sentence=sentence) # (num_tokens, hidden_dim)
        
        word_embedding_1d = []
        for word_data in word_data_1d:
            word_embedding = token_embedding_1d[word_data["token_range"][0]:word_data["token_range"][1]].mean(dim=0)
            word_embedding_1d.append(word_embedding)
        
        return word_embedding_1d #(num_words, hidden_dim)

    def get_word_embedding_2d(self, sentences: List[str], word_data_2d: List[List[dict]]=None, token_embedding_2d=None) :
        """
        Generates word-level embeddings for a batch of sentences.

        Args:
            sentences (List[str]): A list of sentences.

        Returns:
            List[List[torch.Tensor]]: Word embeddings for each sentence.
        """
        if token_embedding_2d is None:
            token_embedding_2d = self.get_token_embedding_2d(sentences=sentences) #(num_sentences, num_tokens, hidden_dim)

        if word_data_2d is None:
            word_data_2d = self.get_word_data_2d(sentences=sentences)

        word_embedding_2d = [] #(num_sentences, num_words, hidden_dim)
        for sentence, token_embedding_1d, word_data_1d in zip(sentences, token_embedding_2d, word_data_2d): 
            word_embedding_2d.append(self.get_word_embedding_1d(sentence=sentence, word_data_1d=word_data_1d, token_embedding_1d=token_embedding_1d))

        return word_embedding_2d #(num_sentences, num_words, hidden_dim)
            
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
        word_data_1d = self.get_word_data_1d(sentence=sentence)
        word_embedding_1d = self.get_word_embedding_1d(sentence=sentence, word_data_1d=word_data_1d)
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
                end = i
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

        return  new_phrase, new_phrase_idx, phrase_embedding 
    
    def get_cossim_phrases(self, phrase_1, phrase_idx_1, sentence_1, phrase_2, phrase_idx_2, sentence_2):
        _, _, emb_1 = self.get_phrase_embedding(phrase=phrase_1, phrase_idx=phrase_idx_1, sentence=sentence_1)
        _, _, emb_2 = self.get_phrase_embedding(phrase=phrase_2, phrase_idx=phrase_idx_2, sentence=sentence_2)
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))
    
    def get_cossim_sentences(self, sentence_1, sentence_2):
        emb_1 = self.get_token_embedding_1d(sentence=sentence_1)[0]
        emb_2 = self.get_token_embedding_1d(sentence=sentence_2)[0]
        return F.cosine_similarity(emb_1.unsqueeze(0), emb_2.unsqueeze(0))