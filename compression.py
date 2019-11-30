import re
import nltk
from nltk.corpus import stopwords

stops_words = stopwords.words("english")[:150]


def clean(body):
    body = body.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    body = body.replace('[  ]{1, }', ' ')
    body = re.sub("\t\n\r", " ", body)
    body = re.sub("( ){2,}", " ", body)
    return body


def compression(body):
    tokens = nltk.word_tokenize(body)
    tokens = [re.sub(r'[\W\s]', '', token) for token in tokens]  # 去掉标点
    tokens = [re.sub(r'[\d+]', '', token) for token in tokens]  # 去掉数字
    empty_spaces = []
    for token in tokens:
        if token == "":
            empty_spaces.append(token)
    for e in empty_spaces:
        tokens.remove(e)

    global stops_words
    stop_words_list = []  # 去掉stopwords
    for token in tokens:
        if token in stops_words:
            stop_words_list.append(token)
    for n_tk in stop_words_list:
        tokens.remove(n_tk)

    return [token.lower() for token in tokens]#大小写