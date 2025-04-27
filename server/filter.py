import heapq
import random
from model.models import RemindersTextResponseSentenceData, RemindersTextResponseData

class RelatedPhrasesFilter():
    def __init__(self):
        pass

    def filter_1(self, related_phrase_data_2d: list, max_unique_sentence: int = 1):
        # For each word, only keep at most <max_unique_sentence> related words in the same sentence
        # Why? Users are reading a sentence: "I love you". There is a sentence in db: "He loves her". 
        # The word "I" will be very closed to "He", "loves", and "her" because 2 sentences have alike meaning.
        # The max_unique_sentence is in case: "I" is closer to "loves" than "He" while "I" should be closer to "He".
        filtered_related_phrase_data_2d = []
        for related_phrase_data_1d in related_phrase_data_2d:
            count_unique_sentences = {}
            filtered_related_phrase_data_1d = []
            for related_phrase_data in related_phrase_data_1d:
                sentence = related_phrase_data.payload["sentence"]
                if count_unique_sentences.get(sentence, 0) < max_unique_sentence:
                    count_unique_sentences[sentence] = count_unique_sentences.get(sentence, 0) + 1
                    filtered_related_phrase_data_1d.append(related_phrase_data)
            
            filtered_related_phrase_data_2d.append(filtered_related_phrase_data_1d)
        
        return filtered_related_phrase_data_2d
    
    def filter_2(self, related_phrase_data_2d: list, max_unique_phrase_sentence: int = 1):
        # A sentence has words, a word has related phrases in other sentences. 
        # A sentence only allows at most <max_unique_phrase_sentence> occurences of a unique pair of related phrase-sentence.  
        # Why? Users are reading a sentence: "I love you". There is a sentence in db: "He loves her".    
        # The words "I", "love", "you" will be very closed to "He" because 2 sentences have alike meaning.
        score_unique_word_sentence = {}
        for related_phrase_data_1d in related_phrase_data_2d:
            for related_phrase_data in related_phrase_data_1d:
                phrase = related_phrase_data.payload["phrase"]
                sentence = related_phrase_data.payload["sentence"]
                score = related_phrase_data.score
                key = f"{phrase} ###ENCODE### {sentence}"

                if key not in score_unique_word_sentence:
                    score_unique_word_sentence[key] = []
                
                # Maintain a min-heap to keep the top scores
                if len(score_unique_word_sentence[key]) < max_unique_phrase_sentence:
                    heapq.heappush(score_unique_word_sentence[key], score)
                elif score > score_unique_word_sentence[key][0]: # If higher than the lowest in the heap
                    heapq.heapreplace(score_unique_word_sentence[key], score)
        
        filtered_related_phrase_data_2d = []
        for related_phrase_data_1d in related_phrase_data_2d:
            filtered_related_phrase_data_1d = []
            for related_phrase_data in related_phrase_data_1d:
                phrase = related_phrase_data.payload["phrase"]
                sentence = related_phrase_data.payload["sentence"]
                score = related_phrase_data.score
                key = f"{phrase} ###ENCODE### {sentence}"
                if score >= score_unique_word_sentence[key][0]:
                    filtered_related_phrase_data_1d.append(related_phrase_data)
            filtered_related_phrase_data_2d.append(filtered_related_phrase_data_1d)

        return filtered_related_phrase_data_2d
    
    def sample(self, related_phrase_data_2d: list, limit=1):
        # each word is allowed to have at most <limit> related phrases
        sampled_related_phrase_data_2d = []
        for related_phrase_data_1d in related_phrase_data_2d:
            if len(related_phrase_data_1d) <= limit:
                sampled_related_phrase_data_2d.append(related_phrase_data_1d)
            else:
                sampled_related_phrase_data_2d.append(random.choices(related_phrase_data_1d, weights=[d.score for d in related_phrase_data_1d], k=limit))
        return sampled_related_phrase_data_2d
    
    def filter(self, related_phrase_data_3d):
        # related_phrase_3d: [sentences_num, words_num, related_phrases_num]
        filtered_related_phrase_data_3d = []
        for related_phrase_data_2d in related_phrase_data_3d:
            filtered_related_phrase_data_2d = self.filter_1(related_phrase_data_2d=related_phrase_data_2d)
            filtered_related_phrase_data_2d = self.filter_2(related_phrase_data_2d=filtered_related_phrase_data_2d)
            filtered_related_phrase_data_2d = self.sample(related_phrase_data_2d=filtered_related_phrase_data_2d)
            filtered_related_phrase_data_3d.append(filtered_related_phrase_data_2d)
        return filtered_related_phrase_data_3d
    
    def sample_reminder(self, sentence_data_1d, limit = 999):
        results: list[RemindersTextResponseData] = []

        for sentence_data in sentence_data_1d:
            sentence = sentence_data["sentence"]
            words =  [word_data["word"] for word_data in sentence_data["word_data_1d"]] 
            word_indices = [word_data["word_idx"] for word_data in sentence_data["word_data_1d"]]
            related_phrase_data_2d = sentence_data["related_phrase_data_2d"]

            # Find words that have at least one related phrase with "reminder"
            valid_words = [
                (i, [related_phrase_data for related_phrase_data in related_phrase_data_2d[i] if "reminder" in related_phrase_data.payload])
                for i in range(len(words))
                if any("reminder" in related_phrase_data.payload for related_phrase_data in related_phrase_data_2d[i])
            ]

            if len(valid_words) == 0:
                continue
            elif len(valid_words) > limit:
                chosen_words = random.sample(valid_words, 3)
            else:
                chosen_words = valid_words
            
            # Choose one related phrase from each selected word
            reminders_data = []
            for word_idx, related_phrase_data_1d in chosen_words:
                related_phrase_data = random.choice(related_phrase_data_1d)
                reminders_data.append(RemindersTextResponseSentenceData(
                    word=words[word_idx],
                    word_idx=word_indices[word_idx],
                    related_phrase=related_phrase_data.payload["phrase"],
                    related_phrase_sentence=related_phrase_data.payload["sentence"],
                    reminder=related_phrase_data.payload["reminder"]
                ))

            results.append(RemindersTextResponseData(sentence=sentence, reminders_data=reminders_data))

        return results



