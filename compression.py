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
    # global english_words
    remove_list = [] # remove stopwords and not English
    # stop_words_list = []  # remove stopwords
    # not_english_words_list = [] # remove the word not English
    for token in tokens:
        # if token in stops_words:
        if token in stops_words or not token.encode('UTF-8').isalpha():
            remove_list.append(token)
    for r_token in remove_list:
        tokens.remove(r_token)
    #     if token not in english_words:
    #         not_english_words_list.append(token)
    #     if token in stops_words:
    #         stop_words_list.append(token)
    # for n_tk in stop_words_list:
    #     tokens.remove(n_tk)

    return [token.lower() for token in tokens] # case folding