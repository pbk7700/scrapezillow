import re
from urlparse import urljoin

from bs4 import BeautifulSoup
from httplib import OK
import requests

from scrapezillow import constants


def _get_sale_info(soup):
    sale_info = {}
    value_wrapper = soup.find("div", id=constants.HOME_VALUE)
    summary_rows = value_wrapper.find_all(class_=re.compile("home-summary-row"))
    for row in summary_rows:
        pricing_re = "(Foreclosure Estimate|Below Zestimate|Rent Zestimate|Zestimate|Sold on)(?:\xae)?:?[\n ]+\$?([\d,\/\w]+)"
        pricing = re.findall(pricing_re, row.text)
        status = re.findall("(For Sale|Auction|Make Me Move|For Rent|Pre-Foreclosure|Off Market)", row.text)
        if pricing:
            property_ = pricing[0][0].strip().replace(" ", "_").lower()
            sale_info[str(property_)] = pricing[0][1]
        elif status:
            sale_info["status"] = status[0]
        elif re.search("\$?[\d,]+", row.text):
            sale_info["price"] = re.findall(r"\$?([\d,]+)", row.text)[0]
    return sale_info


def _get_property_summary(soup):
    def parse_property(regex, property_):
        try:
            results[property_] = re.findall(regex, prop_summary)[0]
        except IndexError:
            pass

    prop_summary = soup.find("div", class_=constants.PROP_SUMMARY_CLASS).text
    results = {}
    parse_property(r"([\d\.]+) beds?", "bedrooms")
    parse_property(r"([\d\.]+) baths?", "bathrooms")
    parse_property(r"([\d,\.]+) sqft", "sqft")
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
    parsed_facts = {}
    for fact in facts:
        if fact.text in constants.HOME_TYPES:
            parsed_facts["home_type"] = fact.text
        elif "Built in" in fact.text:
            parsed_facts["year"] = re.findall(r"Built in (\d+)", fact.text)[0]
        elif "days on Zillow" in fact.text:
            parsed_facts["days_on_zillow"] = re.findall(r"(\d+) days", fact.text)[0]
        elif len(fact.text.split(":")) == 1:
            if not "extras" in parsed_facts:
                parsed_facts["extras"] = []
            parsed_facts["extras"].append(fact.text)
        else:
            string = re.sub("( #|# )", "", fact.text)
            split = string.split(":")
            # Translate facts types to vars_with_underscores and convert unicode to string
            parsed_facts[str(split[0].strip().replace(" ", "_").lower())] = split[1].strip()
    return parsed_facts


def get_raw_html(url, timeout):
    response = requests.get(url, timeout=timeout)
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


def scrape_url(url, zpid, request_timeout):
    """
    Scrape a specific zillow home. Takes either a url or a zpid. If both/neither are
    specified this function will throw an error.
    """
    url = validate_scraper_input(url, zpid)
    soup = BeautifulSoup(get_raw_html(url, request_timeout))
    results = _get_property_summary(soup)
    facts = _parse_facts(_get_fact_list(soup))
    results.update(**facts)
    results.update(**_get_sale_info(soup))
    results["description"] = _get_description(soup)
    return results
