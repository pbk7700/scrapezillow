from argparse import ArgumentParser
from pprint import pprint

from scrapezillow.scraper import scrape_url


def main():
    parser = ArgumentParser()
    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument("--zpid")
    mutex.add_argument("--url")
    args = parser.parse_args()
    pprint(scrape_url(**args.__dict__))
