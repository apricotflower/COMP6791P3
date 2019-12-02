import PARAMETER
from collections import OrderedDict
import os
import ast
import json
# for counting the compression table
terms_num = 0
nonpositional_postings_num = 0


def spimi_invert(block_index):
    """ Generate the inverted index by SPIMI algorithm """
    articles = 0
    block_number = 0
    len_size_leave = len(deal_all_document)
    block_dict = {}
    for (key, value) in deal_all_document.items():
        for term in value:
            if term not in block_dict:
                index_list = [[key, 1]]
                block_dict[term] = index_list
            else:
                has_key = False
                for doc in block_dict[term]:
                    if doc[0] == key:
                        doc[1] = doc[1] + 1
                        has_key = True
                if not has_key:
                    block_dict[term].append([key, 1])

        articles = articles + 1
        len_size_leave = len_size_leave - 1

        if articles >= PARAMETER.BLOCK_SIZE or len_size_leave == 0:
            fo = open(block_index + "BLOCK" + str(block_number) + ".txt", "a+",encoding='utf8')
            keys_list = sorted(block_dict.keys())
            sorted_block_dict = OrderedDict()
            for key_1 in keys_list:
                sorted_block_dict[key_1] = block_dict[key_1]
            i = 1
            len_d = len(sorted_block_dict.items())
            for (key_2, value_2) in sorted_block_dict.items():
                # key_2 = key_2.encode('unicode_escape')
                if len_d == i:
                    fo.write(key_2 + ":" + str(value_2))
                else:
                    fo.write(key_2 + ":" + str(value_2) + "\n")
                i = i + 1
            print("Generate " + block_index +"BLOCK" + str(block_number) + " successfully!")
            block_number = block_number + 1
            block_dict = {}
            articles = 0


def merge_spimi(block_index,merge_block):
    """ Merge the inverted index. """
    print("Start merging ……")
    final_i = 0
    fo = open(merge_block + "II"+ str(final_i) + ".txt", "a+",encoding='utf8')
    final_file_line = 0
    blocks = OrderedDict()
    buffer = OrderedDict()

    for file in os.listdir(block_index):
        blocks[block_index + file] = open(block_index + file,encoding='utf8')

    remain_block_number = len(blocks)

    for block in blocks.values():
        first_line = block.readline()
        term, posting = first_line.rsplit(":", 1)
        buffer[block.name] = [term, ast.literal_eval(posting)]

    while remain_block_number > 0:
        lowest_terms = buffer[min(buffer, key=lambda a: buffer[a][0])][0]
        lowest_block_names = []
        write_down_posting = []
        write_down_line = lowest_terms + ":"
        for (block_name, all_line) in buffer.items():
            if all_line[0] == lowest_terms:
                lowest_block_names.append(block_name)
                write_down_posting = write_down_posting + all_line[1]
        # write_down_posting = list(map(int, write_down_posting))
        for list in write_down_posting:
            list[0] = int(list[0])
            list[1] = int(list[1])
        write_down_posting.sort(key=(lambda x:x[0]))

        if final_file_line == PARAMETER.FINAL_TERMS_SIZE - 1:
            fo.write(write_down_line + str(write_down_posting))
            final_i = final_i + 1
            fo = open(merge_block + "II" + str(final_i) + ".txt", "a+",encoding='utf8')
            final_file_line = 0
        else:
            fo.write(write_down_line + str(write_down_posting) + "\n")

        global terms_num
        global nonpositional_postings_num
        terms_num = terms_num + 1
        nonpositional_postings_num = nonpositional_postings_num + len(write_down_posting)
        final_file_line = final_file_line + 1

        for lowest_block_name in lowest_block_names:
            line = blocks[lowest_block_name].readline()
            if line:
                term, posting = line.rsplit(":", 1)
                buffer[lowest_block_name] = [term, ast.literal_eval(posting)]
            else:
                del buffer[lowest_block_name]
                print(lowest_block_name + " merge finish!")
                remain_block_number = remain_block_number - 1


def generate_ai_df_index():
    search_index = PARAMETER.MERGE_BLOCK_PATH_AI
    outfile = open(PARAMETER.AI_DF, "a+", encoding='utf8')
    try:
        if not os.listdir(search_index):
            print("The index for dictionary is empty, please generate it first! ")
            os._exit(0)
    except FileNotFoundError:
        print("The index for dictionary is empty, please generate it first! ")
        os._exit(0)
    for file in os.listdir(search_index):
        fo = open(search_index + file, encoding='utf8')
        line = fo.readline()
        while line:
            line_term, posting = line.rsplit(":", 1)
            outfile.write(str(line_term) + ":" + str(len(ast.literal_eval(posting))) + "\n")
            line = fo.readline()


def start_spimi(website,block_index, merge_block):
    global deal_all_document
    # fo = open(PARAMETER.DATA)
    # deal_all_document = json.load(fo)
    deal_all_document ={}
    if website == PARAMETER.WEBSITE_CONCORDIA:
        for file in os.listdir(PARAMETER.DATA_PATH):
            fo = open(PARAMETER.DATA_PATH + file)
            deal_all_document.update(json.load(fo))
        fo2 = open('tokens_number.txt', 'w')
    elif website == PARAMETER.WEBSITE_AI:
        for file in os.listdir(PARAMETER.DATA_PATH_AI):
            fo = open(PARAMETER.DATA_PATH_AI + file)
            deal_all_document.update(json.load(fo))
        fo2 = open('tokens_number_ai.txt', 'w')


    i = 1
    len_d = len(deal_all_document.items())
    # document_token_number = {}
    for (key,value) in deal_all_document.items():
        # document_token_number[key] = len(value)
        if len_d == i:
            fo2.write(key+":"+ str(len(value)))
        else:
            fo2.write(key + ":" + str(len(value)) + "\n")
        i = i + 1
    # json.dump(document_token_number, fo)

    if not os.path.exists(block_index):
        os.makedirs(block_index)

    if not os.path.exists(merge_block):
        os.makedirs(merge_block)

    spimi_invert(block_index)
    merge_spimi(block_index,merge_block)

    if website == PARAMETER.WEBSITE_AI:
        generate_ai_df_index()


if __name__ == '__main__':
    start_spimi(PARAMETER.WEBSITE_CONCORDIA,PARAMETER.BLOCK_PATH_CONCORDIA, PARAMETER.MERGE_BLOCK_PATH_CONCORDIA)