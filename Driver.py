import my_crawler
import PARAMETER
import Spimi
import crawler_html

if __name__ == '__main__':
    print("Start crawling concordia")
    # my_crawler.run()
    crawler_html.run()
    print("Finish crawling concordia")

    print("Start SPIMI concordia")
    Spimi.start_spimi(PARAMETER.BLOCK_PATH,PARAMETER.MERGE_BLOCK_PATH)
    print("Finish SPIMI concordia")

