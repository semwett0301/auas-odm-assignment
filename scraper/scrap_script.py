import json
import subprocess

from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

from scrap_module.spiders.imdb import ImdbSpider
from scrap_module.spiders.imdb_movie import ImdbMovieSpider


class ResultManager:
    def __init__(self):
        self._results = []
        dispatcher.connect(self._crawler_results, signal=signals.item_scraped)

    def clear_results(self):
        self._results = []

    def get_results(self):
        return self._results

    def _crawler_results(self, signal, sender, item, spider, **kwargs):
        self._results.append(item)

def run_spider(spider_name, params=None):
    str_params = ', '.join([f"{key}={value}" for key, value in params.items()]) if params else ''
    command = ['scrapy', 'crawl', spider_name, '-a', str_params]
    subprocess.run(command, check=True)

def main():
    # runner = CrawlerRunner(get_project_settings())

    @defer.inlineCallbacks
    def crawl_spiders():
        # result_manager = ResultManager()
        #
        # # yield runner.crawl(ImdbSpider, iterations=1)
        #
        # start_urls = list(map(lambda x: x['url'], result_manager.get_results()))
        # result_manager.clear_results()
        #
        # for url in start_urls:
        #     yield runner.crawl(ImdbMovieSpider, start_url=url)
        #
        # imdb_movies = result_manager.get_results()
        # metacritic_urls = list(map(lambda x: x['meta_link'], imdb_movies))
        #
        # with open('list.json', 'w') as file:
        #     json.dump(imdb_movies, file)
        #
        # result_manager.clear_results()
        #
        # reactor.stop()
        result_manager = ResultManager()

        yield run_spider('imdb', {'iterations': 1})

        start_urls = list(map(lambda x: x['url'], result_manager.get_results()))
        result_manager.clear_results()

        for url in start_urls:
            yield run_spider('imdb_movie', {'start_url': url})

        imdb_movies = result_manager.get_results()
        with open('list.json', 'w') as file:
            json.dump(imdb_movies, file)

    crawl_spiders()

    reactor.run()

if __name__ == '__main__':
    main()