"""Unit tests for Dataset Augmentation"""

import unittest

import os
import sys
import logging

from tests.webscrapper_unittests import WebScrapperUnitTests

assert WebScrapperUnitTests

sys.path.append(os.getcwd())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()