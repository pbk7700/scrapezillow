scrapezillow
==============
![Scraper](http://www.earthmoversmagazine.co.uk/wp-content/uploads/2013/11/8-1024x722.jpg)

Because the Zillow API is rate limited you can just scrape Zillow HTML to get what 
you need. Combined with the undocumented Zillow GetResults API in `flowzillow` this can be a powerful
tool to get all the information you need for home listings without directly going through MLS and 
RETS.

Installation
------------

    pip install scrapezillow

Usage
-----
It's easy.

For the CLI if you know your zpid you can use

    scrapezillow --zpid <zpid>

If you know the URL you'd like to lookup

    scrapezillow --url <url>

And a bunch of results will be input to screen.

For the API if you want to look a home up by zpid

    from scrapezillow.scraper import scrape_url

    results = scrape_url(None, <zpid>, <request timeout>)

If you'd like to look a home up by url

    results = scrape_url(<url>, None, <request timeout>)

That should give you all the data you need. If not feel free to complain to me.
