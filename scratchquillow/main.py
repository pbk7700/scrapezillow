from argparse import ArgumentParser

from scratchquillow.scraper import scrape_url


def main():
    parser = ArgumentParser()
    mutex = parser.add_mutually_exclusive_group(required=True)
    mutex.add_argument("--zpid")
    mutex.add_argument("--url")
    args = parser.parse_args()
    print scrape_url(**args.__dict__)
