import os
import PARAMETER
import ast
import itertools
import re
import math
import copy
import json
from urllib import request
from bs4 import BeautifulSoup

search_dict = dict()
dict_check = dict()
df_ai = dict()
use_ai_df = 0


def check_and_query(query_list, result):
    """  Check the result from and query. If the result is empty, query the combinations of the terms. """
    if len(result) == 0:
        print("No result for this AND query: " + str(query_list) + ", start printing results of smaller size terms in this query ……")
        print("**" * 20)
        i = 1
        shorter_lists = list(itertools.combinations(query_list, len(query_list) - i))
        while len(shorter_lists[0]) > 0:
            results = []
            for shorter_list in shorter_lists:
                shorter_list = list(shorter_list)
                result = multiple_query(shorter_list, PARAMETER.QUERY_AND)
                results.append(result)
                if len(result) != 0:
                    print("Keyword: " + str(shorter_list))
                    for (i1,v) in enumerate(result):
                        result[i1] = v[0]
                    print(str(len(result)) + " documents was found." + "Result: " + str(result))
                    print("**"*10)
            i = i + 1
            shorter_lists = list(itertools.combinations(query_list, len(query_list) - i))


def doc_id_sorted(query_list, result):
    """  In or query, sort the document according to the number of keywords. """
    id_dict = {}
    for id in result:
        for term in query_list:
            for list in search_dict[term]:
                if list[0] == id :
                    if id not in id_dict:
                        id_dict[id] = 1
                    else:
                        id_dict[id] = id_dict[id] + 1
    sorted_id = sorted(id_dict.items(), key= lambda x:x[1],reverse=True)
    print("Order: " + str(sorted_id))


def or_query_each(p1, p2):
    """  or operation of two terms """
    answer = []
    p1_pointer = 0
    p2_pointer = 0

    while len(p1) > p1_pointer and len(p2) > p2_pointer:
        if p1[p1_pointer][0] == p2[p2_pointer][0]:
            answer.append(p1[p1_pointer])
            p1_pointer = p1_pointer + 1
            p2_pointer = p2_pointer + 1
        elif p1[p1_pointer][0] < p2[p2_pointer][0]:
            answer.append(p1[p1_pointer])
            p1_pointer = p1_pointer + 1
        else:
            answer.append(p2[p2_pointer])
            p2_pointer = p2_pointer + 1
    if p1_pointer == len(p1):
        answer = answer + p2[p2_pointer:]
    elif p2_pointer == len(p2):
        answer = answer + p1[p1_pointer:]
    return answer


def and_query_each(p1, p2):
    """ and operation of two terms """
    answer = []
    p1_pointer = 0
    p2_pointer = 0
    while len(p1) > p1_pointer and len(p2) > p2_pointer:
        if p1[p1_pointer][0] == p2[p2_pointer][0]:
            answer.append(p1[p1_pointer])
            p1_pointer = p1_pointer + 1
            p2_pointer = p2_pointer + 1
        elif  p1[p1_pointer][0] < p2[p2_pointer][0]:
            p1_pointer = p1_pointer + 1
        else:
            p2_pointer = p2_pointer + 1
    return answer


def check_exist(query_list):
    """ Check if every terms is existed in the dictionary. """
    exist_list = []
    every_term_exist = True
    for term in query_list:
        posting = search_dict.get(term, None)
        if posting is None:
            print("[ " + str(term) + " ] does not exist in the dictionary! ")
            every_term_exist = False
        else:
            exist_list.append(term)

    if not exist_list:
        print(str(len(exist_list)) + " result exist! input again ……")
        return start_query()
    if not every_term_exist:
        print("Only found " + str(exist_list) + " in the dictionary. \n" + "Start querying result with these " + str(len(exist_list)) + " terms ……" )
        print("**"*30)
        print("Keyword: " + str(exist_list))
    return exist_list


def multiple_query(query_list, operator):
    query_list.sort(key=lambda x: len(search_dict[x]))
    result = search_dict[query_list[0]]
    rest_list = query_list[1:]
    while len(result) != 0 and len(rest_list) != 0:
        if operator == PARAMETER.QUERY_AND:
            result = and_query_each(result, search_dict[rest_list[0]])
        elif operator == PARAMETER.QUERY_OR:
            result = or_query_each(result, search_dict[rest_list[0]])
        rest_list = rest_list[1:]
    return result


def find_ai_df(t):
    dft = -1
    global df_ai
    if df_ai == {}:
        fo = open(PARAMETER.AI_DF, 'r', encoding='utf8')
        line = fo.readline()
        while line:
            term, ai_df = line.split(":")
            if str(term) == str(t):
                # print("Find " + str(t) + " in AIindex !")
                dft = float(ai_df)
            line = fo.readline()
    else:
        try:
            dft = df_ai[t]
        except KeyError:
            pass
    return dft


def compute_RSVd(document, query_list,k1,b):
    """ compute RSVd of one document """
    global use_ai_df
    l_d = int(find_tokens_number(document))
    temp = 0
    for t in query_list:
        tftd = 0
        for newid_pair in search_dict[t]:
            if str(newid_pair[0]) == str(document):
                tftd = newid_pair[1]

        if use_ai_df == "0":
            dft = len(search_dict[t])
        elif use_ai_df == "1":
            dft = find_ai_df(t)

        if dft == -1:
            dft = len(search_dict[t])

        temp = temp+((math.log((n/dft), 10))*(((k1+1)*tftd)/(k1*((1-b)+b*(l_d/l_avc))+tftd)))
    RSVd = temp
    return RSVd


def compute_l_avc(n):
    """ compute Lave """
    sum = 0
    fo = open(PARAMETER.TOKEN_NUMBER_CONCORDIA, 'r',encoding='utf8')
    line = fo.readline()
    while line:
        newid,token_number = line.split(":")
        sum = sum + int(token_number)
        line = fo.readline()
    return sum/n


def bm25_query(query_list):
    global dict_check
    global use_ai_df
    """ bm25 query sort, recommend use k1 = 1.2(>0) and b = 0.75 (0=<b=<1) """

    print("Do you want to use AIindex df ? Yes input 1 , No input 0")
    use_ai_df = input()

    while use_ai_df != "1" and use_ai_df != "0":
        print("Do you want to use AIindex df ? Yes input 1 , No input 0")
        use_ai_df = input()

    print("Input k1: ")
    k1=float(input())
    print("Input b: ")
    b =float(input())

    documents = multiple_query(query_list, PARAMETER.QUERY_OR)
    copy_doc = copy.deepcopy(documents)
    for (i,v) in enumerate(copy_doc):
        copy_doc[i] = v[0]
    documents_RSVd = {}
    for d in copy_doc:
        documents_RSVd[d] = compute_RSVd(str(d), query_list,k1,b)
    sorted_RSVd = sorted(documents_RSVd.items(), key=lambda x: x[1], reverse=True)
    print(str(len(sorted_RSVd)) + " documents were ranked.")
    ans_url_list = []
    counter = 0
    for doc in sorted_RSVd:
        # print("doc_id: " + str(doc[0]) + " rank_val: " + str(doc[1]))
        ans_url = str(dict_check[str(doc[0])].split(".html")[0] + ".html")
        ans_url_list.append(ans_url)
        print("TOP: " + str(counter))
        print("doc_id: " + str(doc[0]) + " rank_val: " + str(doc[1]) + "\n" + "url: " + ans_url)
        counter = counter + 1

    print("Do you want to try to find the exact answer automatically? Input 1 for yes 0 for No ")
    check_e = input()
    if check_e == "1":
        check_exact_answer(query_list, ans_url_list)


def get_url_content(url):
    # print(url)
    content = ""
    try:
        text = request.urlopen(url)
        soup = BeautifulSoup(text, "html.parser")
        soup_tags = [soup.div, soup.span, soup.p, soup.a, soup.h1, soup.h2, soup.h3, soup.h4, soup.h5, soup.h6, soup.li]
        for soup_tag in soup_tags:
            if soup_tag:
                content = content + soup_tag.text.strip() + " "
    except BaseException:
        # print("Error in page! ")
        pass
    return content


def find_exact_ans_helper(file_list, content):
    exact_ans_list = []
    fo = open(file_list, 'r', encoding='utf8')
    line = fo.readline()
    while line:
        if line.lower().strip("\n") in content.lower():
            exact_ans_list.append(line)
        line = fo.readline()
    print("Print exact answers are: ")
    for exact_a in exact_ans_list:
        print(str(exact_a).strip("\n"))


def check_exact_answer(query_list, ans_url):
    content = ""
    for i in range(0, 10):
        content = content + get_url_content(ans_url[i])
    for term in query_list:
        if term.lower() in PARAMETER.DEPARTMENT:
            find_exact_ans_helper(PARAMETER.DEPARTMENT_LIST, content)
        if term.lower() in PARAMETER.RESEARCHER:
            find_exact_ans_helper(PARAMETER.RESEARCHER_LIST, content)
        if term.lower() in PARAMETER.CONDUCT:
            find_exact_ans_helper(PARAMETER.CONDUCT_LIST, content)


def compute_tfidf(document,query_list):
    global use_ai_df
    temp = 0
    for t in query_list:
        tftd = 0
        for newid_pair in search_dict[t]:
            if str(newid_pair[0]) == str(document):
                tftd = newid_pair[1]

        if use_ai_df == "0":
            dft = len(search_dict[t])
        elif use_ai_df == "1":
            dft = find_ai_df(t)

        if dft == -1:
            dft = len(search_dict[t])

        temp = temp + math.log((n / dft), 10)*tftd
    return temp


def tf_idf_query(query_list):
    global dict_check
    global use_ai_df

    print("Do you want to use AIindex df ? Yes input 1 , No input 0")
    use_ai_df = input()

    while use_ai_df != "1" and use_ai_df != "0":
        print("Do you want to use AIindex df ? Yes input 1 , No input 0")
        use_ai_df = input()

    documents = multiple_query(query_list, PARAMETER.QUERY_OR)
    copy_doc = copy.deepcopy(documents)
    for (i,v) in enumerate(copy_doc):
        copy_doc[i] = v[0]
    documents_tfidf = {}
    for d in copy_doc:
        documents_tfidf[d] = compute_tfidf(str(d), query_list)
    sorted_tfidf = sorted(documents_tfidf.items(), key=lambda x: x[1], reverse=True)
    print(str(len(sorted_tfidf)) + " documents were ranked.")
    ans_url_list = []
    counter = 0
    for doc in sorted_tfidf:
        url = str(dict_check[str(doc[0])].split(".html")[0]+ ".html")
        ans_url_list.append(url)
        print("TOP: " + str(counter))
        print("doc_id: " + str(doc[0]) + " rank_val: " + str(doc[1]) + "\n" + "url: " + url)
        counter = counter + 1

    print("Do you want to try to find the exact answer automatically? Input 1 for yes 0 for No ")
    check_e = input()
    if check_e == "1":
        check_exact_answer(query_list, ans_url_list)


def deal_with_query(query):
    """  Decide the terms and operator in the query. """
    query_list = []
    query_list_or = []
    query_list_and = []
    operator = ""
    query_raw = query.split(" ")
    if len(query_raw) == 1:
        query_list = query_raw
        operator = PARAMETER.QUERY_SINGLE
    elif query_raw[0] == PARAMETER.QUERY_BM25:
        query_list = query_raw[1:]
        operator = PARAMETER.QUERY_BM25
    elif query_raw[0] == PARAMETER.QUERY_TFIDF:
        query_list = query_raw[1:]
        operator = PARAMETER.QUERY_TFIDF
    else:
        if query_raw[1] == PARAMETER.QUERY_OR:
            query_list_or.append(query_raw[0])
            for (i, v) in enumerate(query_raw):
                if v == PARAMETER.QUERY_OR:
                    query_list_or.append(query_raw[i + 1])
            operator = PARAMETER.QUERY_OR
            query_list = query_list_or
        elif query_raw[1] == PARAMETER.QUERY_AND:
            query_list_and.append(query_raw[0])
            for (i, v) in enumerate(query_raw):
                if v == PARAMETER.QUERY_AND:
                    query_list_and.append(query_raw[i + 1])
            operator = PARAMETER.QUERY_AND
            query_list = query_list_and
    query_list = [re.sub(r'[\W\s]', '', token) for token in query_list]
    return query_list, operator


def get_search_dict(query_list):
    print("Getting ……")
    search_index = PARAMETER.MERGE_BLOCK_PATH_CONCORDIA
    global search_dict
    search_dict = {}
    try:
        if not os.listdir(search_index):
            print("The index for dictionary is empty, please generate it first! ")
            os._exit(0)
    except FileNotFoundError:
        print("The index for dictionary is empty, please generate it first! ")
        os._exit(0)
    for term in query_list:
        for file in os.listdir(search_index):
            fo = open(search_index + file,encoding='utf8')
            line = fo.readline()
            has_term = False
            while line:
                line_term, posting = line.rsplit(":", 1)
                if line_term == term:
                    search_dict[term] = ast.literal_eval(posting)
                    has_term = True
                    break
                line = fo.readline()
            if has_term:
                break
    # print(search_dict)


def prepare_bm25_para():
    """ prepare n and l_avc for bm25 """
    global n
    global l_avc
    count = -1
    for count,line in enumerate(open(PARAMETER.TOKEN_NUMBER_CONCORDIA)): pass
    n = count+1
    l_avc = compute_l_avc(n)


def find_url():
    global dict_check
    dict_check = {}
    for file in os.listdir(PARAMETER.DICT_PATH):
        fo = open(PARAMETER.DICT_PATH + file,encoding='utf8')
        dict_check.update(json.load(fo))


def find_tokens_number(find_newid):
    """ find l_d """
    answer = None
    fo = open(PARAMETER.TOKEN_NUMBER_CONCORDIA, 'r',encoding='utf8')
    line = fo.readline()
    while line:
        newid,token_number = line.split(":")
        if str(newid) == str(find_newid):
            answer = token_number
        line = fo.readline()
    return answer


def load():
    print("Getting ……")
    search_index = PARAMETER.MERGE_BLOCK_PATH_CONCORDIA
    global search_dict
    search_dict = {}
    try:
        if not os.listdir(search_index):
            print("The index for dictionary is empty, please generate it first! ")
            os._exit(0)
    except FileNotFoundError:
        print("The index for dictionary is empty, please generate it first! ")
        os._exit(0)
    try:
        for file in os.listdir(search_index):
            fo = open(search_index + file, encoding='utf8')
            line = fo.readline()
            while line:
                line_term, posting = line.rsplit(":", 1)
                search_dict[line_term] = ast.literal_eval(posting)
                line = fo.readline()
    except BaseException:
        print("The file is too big to load into memory, now change to a model which can save memory……")
        pass

    global df_ai
    df_ai = {}
    try:
        fo = open(PARAMETER.AI_DF, 'r', encoding='utf8')
        line = fo.readline()
        while line:
            term, ai_df = line.split(":")
            df_ai[term] = float(ai_df)
            line = fo.readline()
    except BaseException:
        print("The file is too big to load into memory, now change to a model which can save memory……")
        pass

    # print(search_dict)


def start_query():
    global search_dict
    load()
    find_url()
    print("**"*40)
    print("Please input query: ")
    query = input().lower().strip()
    while query.lower() != PARAMETER.EXIT:
        try:
            query_list, operator = deal_with_query(query)
            if search_dict == {}:
                get_search_dict(query_list)
            prepare_bm25_para()
        except IndexError:
            print("Wrong query format! Input again!")
            start_query()
        print("Start " + operator.upper() + " query")
        print("Keyword: " + str(query_list))
        query_list = check_exist(query_list)
        if operator == PARAMETER.QUERY_AND or operator == PARAMETER.QUERY_OR or operator == PARAMETER.QUERY_SINGLE:
            result = multiple_query(query_list, operator)
            for (i, v) in enumerate(result):
                result[i] = v[0]
            print(str(len(result)) + " documents were found." + "Total result: " + str(result))
            for index in result:
                print(dict_check[str(index)].split(".html")[0]+ ".html")
            if operator == PARAMETER.QUERY_AND:
                check_and_query(query_list, result)
            elif operator == PARAMETER.QUERY_OR:
                doc_id_sorted(query_list, result)
        elif operator == PARAMETER.QUERY_BM25:
            bm25_query(query_list)
        elif operator == PARAMETER.QUERY_TFIDF:
            tf_idf_query(query_list)
        else:
            print("Operator wrong! Input again!")
        print("**" * 40)
        search_dict = {}
        query = input().lower().strip()

    os._exit(0)


if __name__ == '__main__':
    start_query()