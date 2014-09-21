#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1"


setup(
    name="scrapezillow",
    author="Gregory Rehm",
    version=__version__,
    description="A zillow scraper",
    packages=find_packages(),
    package_data={"*": ["*.html"]},
    install_requires=[
        "beautifulsoup4",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "scrapezillow=scrapezillow.main:main",
        ]
    }
)
