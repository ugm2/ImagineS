"""Unit tests for WebScrapper class"""

import unittest
import os

from dataset_augmentation import WebScrapper
from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException

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
        self.driver_path = './tests/test_artifacts/chromedriver'
        os.chmod(self.driver_path, 755)

    def test_webscrapper_init(self):
        """Unit tests for WebScrapper"""
        driver_type = 'chrome'
        webscrapper = WebScrapper(driver_type, self.driver_path)
        self.assertIsInstance(webscrapper, WebScrapper)
        self.assertIsInstance(webscrapper.driver, Chrome)

    def test_webscrapper_search_images(self):
        """Unit tests for WebScrapper"""
        driver_type = 'chrome'
        webscrapper = WebScrapper(driver_type, self.driver_path)
        query = 'test'
        max_links_to_fetch = 3
        sleep_between_interactions = 1
        image_urls = webscrapper.search_images(query, max_links_to_fetch, sleep_between_interactions)
        self.assertIsInstance(image_urls, set)
        self.assertEqual(len(image_urls), max_links_to_fetch)
        # Check that URLs are valid
        for url in image_urls:
            self.assertTrue(url.startswith('http'))

    def test_webscrapper_search_images_with_invalid_driver_type(self):
        """Unit tests for WebScrapper"""
        driver_type = 'invalid'
        with self.assertRaises(ValueError):
            WebScrapper(driver_type, self.driver_path)
        
    def test_webscrapper_search_images_with_invalid_driver_path(self):
        """Unit tests for WebScrapper"""
        driver_type = 'chrome'
        driver_path = './tests/test_artifacts/invalid_driver_path'
        with self.assertRaises(WebDriverException):
            WebScrapper(driver_type, driver_path)
