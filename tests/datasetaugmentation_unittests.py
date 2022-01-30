"""Unit tests for DataAugmentation class"""

import unittest
from unittest.mock import patch
import os
import shutil

from dataset_augmentation.core import DatasetAugmentation, WebScrapper
from selenium.webdriver import Chrome
from selenium.common.exceptions import WebDriverException

import logging

# Set up logging
logging.basicConfig(level=os.getenv("LOGGER_LEVEL", logging.WARNING))
logger = logging.getLogger("Dataset WebScrapper UnitTests")

class WebScrapperMock(WebScrapper):
    """Mock class for WebScrapper"""

    def __init__(self, driver_type, driver_path):
        """Mock class for WebScrapper"""
        pass

    def search_images(self, query, max_links_to_fetch, sleep_between_interactions):
        """Mock class for WebScrapper"""
        toy_image_urls = ['https://www.toyimageurl.com' for _ in range(max_links_to_fetch)]
        return set(toy_image_urls)

class DataAugmentationUnitTests(unittest.TestCase):
    """Unit tests for DataAugmentation"""

    @classmethod
    def setUpClass(cls):
        """Set up all tests."""
        super(DataAugmentationUnitTests, cls).setUpClass()

    def setUp(self):
        """Set up all tests."""
        pass

    @patch('dataset_augmentation.core.WebScrapper', WebScrapperMock)
    def test_data_augmentation_init(self):
        """Unit tests for DataAugmentation"""
        data_augmentation = DatasetAugmentation(
            driver_type='chrome',
            driver_path='path_to/chromedriver',
        )
        self.assertIsInstance(data_augmentation, DatasetAugmentation)
        self.assertIsInstance(data_augmentation.driver, WebScrapper)

    @patch('dataset_augmentation.core.DatasetAugmentation._persist_images')
    @patch('dataset_augmentation.core.DatasetAugmentation.resize_images')
    @patch('dataset_augmentation.core.WebScrapper', WebScrapperMock)
    def test_data_augmentation_augment_dataset(self, resize_images_mock, persist_images_mock):
        """Unit tests for DataAugmentation"""

        # Mocks
        persist_images_mock.return_value = None
        resize_images_mock.return_value = None


        data_augmentation = DatasetAugmentation(
            driver_type='chrome',
            driver_path='path_to/chromedriver',
        )
        label_queries = {
            'test_label_1': ['test_query_1_1'],
            'test_label_2': ['test_query_2_1', 'test_query_2_2'],
        }
        output_directory = './tests/test_artifacts/tmp/'
        max_links_to_fetch = 3
        sleep_between_interactions = 1
        image_shape = (224, 224)
        resize_images = False
        
        data_augmentation.augment_dataset(
            label_queries,
            output_directory,
            max_links_to_fetch,
            image_shape,
            resize_images,
            sleep_between_interactions
        )

        # Assert methods have been called
        self.assertTrue(persist_images_mock.called)
        self.assertFalse(resize_images_mock.called)
        # Assert folders have been created
        self.assertTrue(os.path.exists(output_directory))
        self.assertTrue(os.path.exists(output_directory + 'test_label_1'))
        self.assertTrue(os.path.exists(output_directory + 'test_label_2'))

        # Erase folder
        shutil.rmtree(output_directory)

        # Resize images True

        resize_images = True
        data_augmentation.augment_dataset(
            label_queries,
            output_directory,
            max_links_to_fetch,
            image_shape,
            resize_images,
            sleep_between_interactions
        )

        # Assert methods have been called
        self.assertTrue(persist_images_mock.called)
        self.assertTrue(resize_images_mock.called)
        # Assert folders have been created
        self.assertTrue(os.path.exists(output_directory))
        self.assertTrue(os.path.exists(output_directory + 'test_label_1'))
        self.assertTrue(os.path.exists(output_directory + 'test_label_2'))

        # Erase folder
        shutil.rmtree(output_directory)
        
