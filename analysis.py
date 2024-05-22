import pandas as pd
import nltk
from textblob import TextBlob
from collections import defaultdict
import os

# Define stop words (modify or replace with your list)
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('cmudict')
def read_stopwords(stopword_dir):
  """
  Reads stopwords from multiple text files in a directory (one word per line).

  Args:
      stopword_dir (str): Path to the directory containing stopword files.

  Returns:
      set: Set of stopwords (to avoid duplicates).
  """
  stopwords = set()
  for filename in os.listdir(stopword_dir):
    if filename.endswith(".txt"):
      filepath = os.path.join(stopword_dir, filename)
      with open(filepath, 'r', encoding='latin-1') as f:
        for line in f:
          stopwords.add(line.strip())  # Remove leading/trailing whitespace
  return stopwords

def read_sentiment_words(sentiment_file, polarity):
  """
  Reads sentiment words from a text file (one word per line).

  Args:
      sentiment_file (str): Path to the sentiment word text file.
      polarity (str): "positive" or "negative" to indicate sentiment.

  Returns:
      list: List of sentiment words.
  """
  sentiment_words = []
  with open(sentiment_file, 'r', encoding='latin-1') as f:
    for line in f:
      sentiment_words.append(line.strip())
  return sentiment_words

# Define stopwords and sentiment words paths (modify as needed)
stopword_dir = "StopWords/"
positive_words_file = "MasterDictionary/positive-words.txt"
negative_words_file = "MasterDictionary/negative-words.txt"

# Read stopwords and sentiment words
stop_words = read_stopwords(stopword_dir)
positive_words = read_sentiment_words(positive_words_file, "positive")
negative_words = read_sentiment_words(negative_words_file, "negative")


def process_text(text_file, url_id):
  with open(text_file, 'r') as f:
      text = f.read()

    # Clean text
  cleaned_text = " ".join([word.lower() for word in text.split() if word not in stop_words and word.isalpha()])
  tokens = cleaned_text.split()

  # Sentiment analysis
  blob = TextBlob(cleaned_text)
  positive_score = sum([1 for word in tokens if word in positive_words])
  negative_score = sum([1 for word in tokens if word in negative_words]) * -1  # convert to positive value
  polarity_score = (positive_score - negative_score) / (positive_score + negative_score + 0.000001)
  subjectivity_score = (positive_score + negative_score) / (len(tokens) + 0.000001)

  # Readability analysis
  num_sentences = len(cleaned_text.split('.'))
  average_sentence_length = len(tokens) / num_sentences if num_sentences > 0 else 0

  complex_words = 0
  for word in tokens:
    if word.isalpha():
      try:
        # Access pronunciations for the word
        pronunciations = nltk.corpus.cmudict.dict()[word]
        # Check if any pronunciation has more than 2 syllables
        if any(len(phoneme) > 2 for phoneme in pronunciations[0]):
          complex_words += 1
      except KeyError:
        # Handle cases where the word is not found in the dictionary
        pass
  percent_complex_words = complex_words / len(tokens) if len(tokens) > 0 else 0
  fog_index = 0.4 * (average_sentence_length + percent_complex_words)

  # Word-level analysis
  word_count = len(tokens)
  syllable_count = sum([len([syl for syl in word if syl in 'aeiouAEIOU']) for word in tokens])
  average_word_length = sum(len(word) for word in tokens) / word_count if word_count > 0 else 0

  personal_pronouns = sum([text.count(pronoun) for pronoun in ["i", "we", "my", "ours", "us"]]) - text.count("US")  # exclude country name

  # Calculate additional values
  avg_words_per_sentence = word_count / num_sentences if num_sentences > 0 else 0

  # Return results dictionary
  url = pd.read_csv("Input.csv")[pd.read_csv("Input.csv")["URL_ID"] == url_id]["URL"].values[0]
  return {
    "URL_ID": url_id,
    "URL": url,
    "POSITIVE SCORE": positive_score,
    "NEGATIVE SCORE": negative_score,
    "POLARITY SCORE": polarity_score,
    "SUBJECTIVITY SCORE": subjectivity_score,
    "AVG SENTENCE LENGTH": average_sentence_length,
    "PERCENTAGE OF COMPLEX WORDS": percent_complex_words,
    "FOG INDEX": fog_index,
    "AVG NUMBER OF WORDS PER SENTENCE": avg_words_per_sentence,
    "COMPLEX WORD COUNT": complex_words,
    "WORD COUNT": word_count,
    "SYLLABLE PER WORD": syllable_count,
    "PERSONAL PRONOUNS": personal_pronouns,
    "AVG WORD LENGTH": average_word_length,
    
  }

# Download NLTK resources if needed


# Process text files and store results
results = []
for url_id in pd.read_csv("Input.csv")["URL_ID"]:
  text_file = f"scraping/{url_id}.txt"
  result = process_text(text_file, url_id)
  results.append(result)

# Save results to excel
df = pd.DataFrame(results)
df.to_excel("Output_Data_Structure.xlsx", index=False)

print("Textual", df)
