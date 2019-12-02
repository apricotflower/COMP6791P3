import PARAMETER
import html_handler
import Spimi
import os
import json


def generate_concordia_index():
    print("Start crawling concordia")
    # my_crawler.run()
    html_handler.run(PARAMETER.RAW_PATH_CONCORDIA, PARAMETER.DATA, PARAMETER.DICT)
    print("Finish crawling concordia")

    print("Start SPIMI concordia")
    Spimi.start_spimi(PARAMETER.WEBSITE_CONCORDIA, PARAMETER.BLOCK_PATH_CONCORDIA, PARAMETER.MERGE_BLOCK_PATH_CONCORDIA)
    print("Finish SPIMI concordia")

    if not os.path.exists(PARAMETER.REQUIRMENT_PATH):
        os.makedirs(PARAMETER.REQUIRMENT_PATH)

    output_file = open(PARAMETER.REQUIRMENT_CONCORDIA_INDEX,"a+",encoding='utf8')
    for file in os.listdir(PARAMETER.DATA_PATH):
        fo = open(PARAMETER.DATA_PATH + file,encoding='utf8')
        data_dict = json.load(fo)
        for (key, value) in data_dict.items():
            output_file.write(str(key) + ":" + str(value) + "\n")


if __name__ == '__main__':
    generate_concordia_index()