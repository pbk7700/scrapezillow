import re
from urlparse import urljoin

from bs4 import BeautifulSoup
from httplib import OK
import requests

from scratchquillow import constants


def _get_bed_bath_sqrft(soup):
    def parse_property(regex, property_):
        try:
            results[property_] = re.findall(regex, prop_summary)[0]
        except IndexError:
            pass

    prop_summary = soup.find("div", class_=constants.PROP_SUMMARY_CLASS).text
    results = {}
    parse_property(r"(\d+) beds?", "bedrooms")
    parse_property(r"(\d+) baths?", "bathrooms")
    parse_property(r"(\d+,?\d+) sqft", "sqft")
    parse_property(r"((?:[A-Z]\w+ ?){1,}), [A-Z]{2}", "city")
    parse_property(r"(?:[A-Z]\w+ ?){1,}, ([A-Z]{2})", "state")
    parse_property(r"[A-Z]{2} (\d{5}-?(?:\d{4})?)", "zipcode")
    return results


def _get_description(soup):
    return soup.find("div", class_=constants.DESCRIPTION).text


def _get_fact_list(soup):
    groups = soup.find_all("ul", constants.FACT_GROUPING)
    facts = []
    for group in groups:
        facts.extend(group.find_all(class_=constants.INDIVIDUAL_FACT))
    return facts


def _parse_facts(facts):
    fact_copy = list(facts)
    parsed_facts = {}
    for fact in facts:
        # More home types to come
        if fact.text in ("Single Family", "Condo"):
            parsed_facts["home_type"] = fact.text
        elif "Built in" in fact.text:
            parsed_facts["year"] = re.findall(r"Built in (\d+)", fact.text)[0]
        else:
            string = re.sub("( #|# )", "", fact.text)
            split = string.split(":")
            # For debugging only right now
            if len(split) != 2:
                import pdb
                pdb.set_trace()
            parsed_facts[split[0].strip().replace(" ", "_").lower()] = split[1].strip()
    return parsed_facts


def get_raw_html(url):
    response = requests.get(url)
    if response.status_code != OK:
        raise Exception("You received a {} error. Your content {}".format(
            response.status_code, response.content
        ))
    elif response.url == constants.ZILLOW_HOMES_URL:
        raise Exception(
            "You were redirected to {} perhaps this is because your original url {} was "
            "unable to be found".format(constants.ZILLOW_HOMES_URL, url)
        )
    else:
        return response.content


def validate_scraper_input(url, zpid):
    if url and zpid:
        raise ValueError("You cannot specify both a url and a zpid. Choode one or the other")
    elif not url and not zpid:
        raise ValueError("You must specify either a zpid or a url of the home to scrape")
    if url and "homedetails" not in url:
        raise ValueError(
            "This program only supports gathering data for homes. Please Specify your url as "
            "http://zillow.com/homedetails/<zpid>_zpid"
        )
    return url or urljoin(constants.ZILLOW_URL, "homedetails/{}_zpid".format(zpid))


def scrape_url(url, zpid):
    """
    Scrape a specific zillow home. Takes either a url or a zpid. If both/neither are
    specified this function will throw an error.
    """
    url = validate_scraper_input(url, zpid)
    soup = BeautifulSoup(get_raw_html(url))
    results = _get_bed_bath_sqrft(soup)
    facts = _parse_facts(_get_fact_list(soup))
    results.update(**facts)
    results["description"] = _get_description(soup)
    return results
