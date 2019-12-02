from bs4 import BeautifulSoup
import compression
import os
import PARAMETER
import json
from nltk.corpus import words

index_num = 0
url_dict = dict()
contentDict = dict()
english_words = words.words()


def create_dict(fileName):
    global index_num
    global english_words
    try:
        content = ""
        # fileName = r'C:\Users\liang\Desktop\www.concordia.ca\ginacody\research\ai.html'
        fo = open(fileName, 'r', encoding='utf-8',errors="ignore")
        text = fo.read()
        soup = BeautifulSoup(text, "html.parser")
        soup_tags = [soup.div, soup.span, soup.p,soup.a, soup.h1, soup.h2, soup.h3, soup.h4, soup.h5, soup.h6, soup.li]
        for soup_tag in soup_tags:
            if soup_tag:
                content = content + soup_tag.text.strip() + " "
                # print(soup_tag.text.strip())
    except BaseException:
        print("Error in open Html file")
        pass

    if content:
        content = compression.compression(content)
        # print(content)
        index_num = index_num + 1
        url = "https://" + fileName.replace("\\","/")
        # print(url)
        url_dict[index_num] = url
        # print(content)
        contentDict[index_num] = content


def run(path, data, dict):
    if not os.path.exists(PARAMETER.DATA_PATH):
        os.makedirs(PARAMETER.DATA_PATH)

    if not os.path.exists(PARAMETER.DICT_PATH):
        os.makedirs(PARAMETER.DICT_PATH)

    if not os.path.exists(PARAMETER.DATA_PATH_AI):
        os.makedirs(PARAMETER.DATA_PATH_AI)

    if not os.path.exists(PARAMETER.DICT_PATH_AI):
        os.makedirs(PARAMETER.DICT_PATH_AI)

    dict_num = 0

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            # if name.rsplit('.', 1)[1] == "png" or name.rsplit('.', 1)[1] == "jpg":
            #     continue
            if not name.startswith('.'):
                filename = os.path.join(root, name)
                print(filename)
                create_dict(filename)
                if len(contentDict) == PARAMETER.BLOCK_SIZE:
                    outfile = open(data + str(dict_num) + ".json", 'w',encoding='utf8')
                    json.dump(contentDict, outfile)
                    fo = open(dict + str(dict_num) + ".json", 'w',encoding='utf8')
                    json.dump(url_dict, fo)

                    dict_num = dict_num + 1
                    contentDict.clear()
                    url_dict.clear()
                    outfile.close()
                    fo.close()

    if len(contentDict) > 0:
        outfile = open(data + str(dict_num) + ".json", 'w',encoding='utf8')
        json.dump(contentDict, outfile)
        fo = open(dict + str(dict_num) + ".json", 'w',encoding='utf8')
        json.dump(url_dict, fo)
        contentDict.clear()
        url_dict.clear()
        outfile.close()
        fo.close()

        # for name in dirs:
        #     if not name.startswith('.'):
        #         print(os.path.join(root, name))


if __name__ == '__main__':
    path = PARAMETER.RAW_PATH_CONCORDIA  # 文件夹目录
    data = PARAMETER.DATA
    dict = PARAMETER.DICT
    run(path, data, dict)