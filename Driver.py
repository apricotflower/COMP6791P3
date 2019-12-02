import other_crawler.my_crawler
import PARAMETER
import Spimi
import crawler_html
import ai_index_generate

if __name__ == '__main__':
    print("Start crawling concordia")
    # my_crawler.run()
    crawler_html.run(PARAMETER.RAW_PATH_CONCORDIA,PARAMETER.DATA,PARAMETER.DICT)
    print("Finish crawling concordia")

    print("Start SPIMI concordia")
    Spimi.start_spimi(PARAMETER.WEBSITE_CONCORDIA,PARAMETER.BLOCK_PATH_CONCORDIA, PARAMETER.MERGE_BLOCK_PATH_CONCORDIA)
    print("Finish SPIMI concordia")

    ai_index_generate.generate_ai_index()
