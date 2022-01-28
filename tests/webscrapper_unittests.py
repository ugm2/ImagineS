"""Unit tests for WebScrapper"""

import unittest
import os

from dataset_augmentation.core import WebScrapper

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
