import re
import nltk
from nltk.corpus import stopwords
from nltk.corpus import words

stops_words = stopwords.words("english")[:150]
# english_words = words.words()


def clean(body):
    body = body.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    body = body.replace('[  ]{1, }', ' ')
    body = re.sub("\t\n\r", " ", body)
    body = re.sub("( ){2,}", " ", body)
    return body


def compression(body):
    tokens = nltk.word_tokenize(body)
    tokens = [re.sub(r'[\W\s]', '', token) for token in tokens]  # remove punctuation
    tokens = [re.sub(r'[\d+]', '', token) for token in tokens]  # remove number
    empty_spaces = []
    for token in tokens:
        if token == "":
            empty_spaces.append(token)
    for e in empty_spaces:
        tokens.remove(e)

    global stops_words
    remove_list = [] # remove stopwords and not English words
    for token in tokens:
        if token in stops_words or not token.encode('UTF-8').isalpha():
            remove_list.append(token)
    for r_token in remove_list:
        tokens.remove(r_token)
    return [token.lower() for token in tokens] # case folding
