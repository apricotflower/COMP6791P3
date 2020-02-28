import PARAMETER
import html_handler
import Spimi
import os
import json


def generate_ai_index():
    print("Start crawling AI")
    # my_crawler.run()
    html_handler.run(PARAMETER.RAW_PATH_AI, PARAMETER.DATA_AI, PARAMETER.DICT_AI)
    print("Finish crawling AI")

    print("Start SPIMI AI")
    Spimi.start_spimi(PARAMETER.WEBSITE_AI, PARAMETER.BLOCK_PATH_AI, PARAMETER.MERGE_BLOCK_PATH_AI)
    print("Finish SPIMI AI")

    if not os.path.exists(PARAMETER.REQUIRMENT_PATH):
        os.makedirs(PARAMETER.REQUIRMENT_PATH)

    output_file = open(PARAMETER.REQUIRMENT_AI_INDEX,"a+",encoding='utf8')
    for file in os.listdir(PARAMETER.DATA_PATH_AI):
        fo = open(PARAMETER.DATA_PATH_AI + file,encoding='utf8')
        data_dict = json.load(fo)
        for (key, value) in data_dict.items():
            output_file.write(str(key) + ":" + str(value) + "\n")


if __name__ == '__main__':
    generate_ai_index()