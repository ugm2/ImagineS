"""Unit tests for WebScrapper class"""

import unittest
import os

from imagines import WebScrapper
from selenium.webdriver import Chrome

import logging

# Set up logging
logging.basicConfig(level=os.getenv("LOGGER_LEVEL", logging.WARNING))
logger = logging.getLogger("Dataset WebScrapper UnitTests")

class WebScrapperUnitTests(unittest.TestCase):
    """Unit tests for WebScrapper"""

    @classmethod
    def setUpClass(cls):
        """Set up all tests."""
        super(WebScrapperUnitTests, cls).setUpClass()

    def setUp(self):
        """Set up all tests."""
        pass

    def test_webscrapper_init(self):
        """Unit tests for WebScrapper"""
        driver_type = 'chrome'
        webscrapper = WebScrapper(driver_type)
        self.assertIsInstance(webscrapper, WebScrapper)
        self.assertIsInstance(webscrapper.driver, Chrome)
        webscrapper.close_session()

    def test_webscrapper_search_images(self):
        """Unit tests for WebScrapper"""
        driver_type = 'chrome'
        webscrapper = WebScrapper(driver_type)
        query = 'test'
        max_links_to_fetch = 3
        sleep_between_interactions = 1
        image_urls = webscrapper.search_images(query, max_links_to_fetch, sleep_between_interactions)
        self.assertIsInstance(image_urls, set)
        self.assertEqual(len(image_urls), max_links_to_fetch)
        # Check that URLs are valid
        for url in image_urls:
            self.assertTrue(url.startswith('http'))
        webscrapper.close_session()

    def test_webscrapper_search_images_with_invalid_driver_type(self):
        """Unit tests for WebScrapper"""
        driver_type = 'invalid'
        with self.assertRaises(ValueError):
            WebScrapper(driver_type)
