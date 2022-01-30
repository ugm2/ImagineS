"""Unit tests for DataAugmentation class"""

import hashlib
import unittest
from unittest.mock import patch
import os
import shutil

from dataset_augmentation import DatasetAugmentation, WebScrapper
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

class DatasetAugmentationUnitTests(unittest.TestCase):
    """Unit tests for DatasetAugmentation"""

    @classmethod
    def setUpClass(cls):
        """Set up all tests."""
        super(DatasetAugmentationUnitTests, cls).setUpClass()

    def setUp(self):
        """Set up all tests."""
        pass

    @patch('dataset_augmentation.core.WebScrapper', WebScrapperMock)
    def test_dataset_augmentation_init(self):
        """Unit tests for DataAugmentation"""
        dataset_augmentation = DatasetAugmentation(
            driver_type='chrome',
            driver_path='path_to/chromedriver',
        )
        self.assertIsInstance(dataset_augmentation, DatasetAugmentation)
        self.assertIsInstance(dataset_augmentation.driver, WebScrapper)

    @patch('dataset_augmentation.core.DatasetAugmentation._persist_images')
    @patch('dataset_augmentation.core.DatasetAugmentation.resize_images')
    @patch('dataset_augmentation.core.WebScrapper', WebScrapperMock)
    def test_dataset_augmentation_augment_dataset(self, resize_images_mock, persist_images_mock):
        """Unit tests for DataAugmentation"""

        # Mocks
        persist_images_mock.return_value = None
        resize_images_mock.return_value = None


        dataset_augmentation = DatasetAugmentation(
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
        
        dataset_augmentation.augment_dataset(
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

        # Resize images True

        resize_images = True
        dataset_augmentation.augment_dataset(
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
        
    @patch('dataset_augmentation.core.WebScrapper', WebScrapperMock)
    @patch('requests.get')
    def test_dataset_augmentation_persist_images(self, get_mock):
        """Unit tests for DataAugmentation"""

        # Load test image from disk
        with open('./tests/test_artifacts/test_image.jpg', 'rb') as f:
            image_data = f.read()

        def get_mock_function(url, timeout, params=None, headers=None):
            """Mock function for requests.get"""
            class MockResponse:
                def __init__(self, image_data):
                    self.content = image_data
                    self.status_code = 200

            return MockResponse(image_data)

        # Mocks
        get_mock.side_effect = get_mock_function

        dataset_augmentation = DatasetAugmentation(
            driver_type='chrome',
            driver_path='path_to/chromedriver',
        )
        image_urls = ['https://www.toyimageurl.com' for _ in range(3)]
        output_directory = './tests/test_artifacts/tmp/'
        dataset_augmentation._persist_images(output_directory, image_urls)

        # Assert folder has been created
        self.assertTrue(os.path.exists(output_directory))

        # Assert methods have been called
        self.assertTrue(get_mock.called)

        # Assert files have been created
        self.assertTrue(os.path.exists(output_directory + hashlib.sha1(image_data).hexdigest()[:10] + '.jpg'))

        # Erase folder
        shutil.rmtree(output_directory)
