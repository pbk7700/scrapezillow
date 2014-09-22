import re
from urlparse import urljoin

from bs4 import BeautifulSoup
from httplib import OK
import requests

from scratchquillow.constants import ZILLOW_HOMES_URL, ZILLOW_URL


def _get_detail():
    pass


def get_raw_html(url):
    response = requests.get(url)
    if response.status_code != OK:
        raise Exception("You received a {} error. Your content {}".format(
            response.status_code, response.content
        ))
    elif response.url == ZILLOW_HOMES_URL:
        raise Exception(
            "You were redirected to {} perhaps this is because your original url {} was "
            "unable to be found".format(ZILLOW_HOMES_URL, url)
        )
    else:
        return response.content


def validate_scraper_input(url, zpid):
    if url and zpid:
        raise ValueError("You cannot specify both a url and a zpid. Choode one or the other")
    elif not url and not zpid:
        raise ValueError("You must specify either a zpid or a url of the home to scrape")
    if "homedetails" not in url:
        raise ValueError("This program only supports gathering data for homes")
     return url or urljoin(ZILLOW_URL, "homedetails/{}_zpid".format(zpid))


def scrape_url(url, zpid):
    """
    Scrape a specific zillow home. Takes either a url or a zpid. If both/neither are
    specified this function will throw an error.
    """
    url = validate_scraper_input(url, zpid)
    soup = BeautifulSoup(get_raw_html(url))
    return {
    }
