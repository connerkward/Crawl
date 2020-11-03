from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
import os

DELETE_DATA_FILES = True # set this to false if you want to stop program and keep previous data
DELETE_LOG_FILES = True  # set to false if you want to keep previous url log file

DATA_FILES = ["data.json", "frontier.shelve.db"]
LOG_FILES = ["Logs/URL_LOG.txt"]

def main(config_file, restart):
    if DELETE_DATA_FILES:
        for file in DATA_FILES:
            if os.path.exists(file):
                os.remove(file)
    if DELETE_LOG_FILES:
        for file in LOG_FILES:
            if os.path.exists(file):
                os.remove(file)
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
