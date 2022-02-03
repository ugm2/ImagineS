"""Unit tests for DataAugmentation class"""

import hashlib
import io
import unittest
from unittest.mock import patch
import os
from PIL import Image
import tempfile

from imagines import DatasetAugmentation, WebScrapper

import logging

# Set up logging
logging.basicConfig(level=os.getenv("LOGGER_LEVEL", logging.WARNING))
logger = logging.getLogger("Dataset WebScrapper UnitTests")

class WebScrapperMock(WebScrapper):
    """Mock class for WebScrapper"""

    def __init__(self, driver_type):
        """Mock class for WebScrapper"""
        pass

    def search_images(self, query, max_links_to_fetch, sleep_between_interactions):
        """Mock class for WebScrapper"""
        toy_image_urls = ['https://www.toyimageurl.com' for _ in range(max_links_to_fetch)]
        return set(toy_image_urls)

    def close_session(self):
        """Mock class for WebScrapper"""
        pass

class DatasetAugmentationUnitTests(unittest.TestCase):
    """Unit tests for DatasetAugmentation"""

    @classmethod
    def setUpClass(cls):
        """Set up all tests."""
        super(DatasetAugmentationUnitTests, cls).setUpClass()

    def setUp(self):
        """Set up all tests."""
        # Tmp dir
        self.tmp_dir = tempfile.mkdtemp()

    @patch('imagines.core.WebScrapper', WebScrapperMock)
    def test_dataset_augmentation_init(self):
        """Unit tests for DataAugmentation"""
        dataset_augmentation = DatasetAugmentation(
            driver_type='chrome',
        )
        self.assertIsInstance(dataset_augmentation, DatasetAugmentation)
        self.assertIsInstance(dataset_augmentation.driver, WebScrapper)

    @patch('imagines.core.DatasetAugmentation._persist_images')
    @patch('imagines.core.DatasetAugmentation.resize_images')
    @patch('imagines.core.WebScrapper', WebScrapperMock)
    def test_dataset_augmentation_augment_dataset(self, resize_images_mock, persist_images_mock):
        """Unit tests for DataAugmentation"""

        # Mocks
        persist_images_mock.return_value = None
        resize_images_mock.return_value = None

        dataset_augmentation = DatasetAugmentation(
            driver_type='chrome',
        )
        label_queries = {
            'test_label_1': ['test_query_1_1'],
            'test_label_2': ['test_query_2_1', 'test_query_2_2'],
        }
        max_links_to_fetch = 3
        sleep_between_interactions = 1
        image_shape = (224, 224)
        resize_images = False
        
        dataset_augmentation.augment_dataset(
            label_queries,
            self.tmp_dir,
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
            self.tmp_dir,
            max_links_to_fetch,
            image_shape,
            resize_images,
            sleep_between_interactions
        )

        # Assert methods have been called
        self.assertTrue(persist_images_mock.called)
        self.assertTrue(resize_images_mock.called)
        
    @patch('imagines.core.WebScrapper', WebScrapperMock)
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
        )
        image_urls = ['https://www.toyimageurl.com' for _ in range(3)]
        output_dir = self.tmp_dir + '/test_output_dir/'
        dataset_augmentation._persist_images(output_dir, image_urls)

        # Assert folder has been created
        self.assertTrue(os.path.exists(output_dir))

        # Assert methods have been called
        self.assertTrue(get_mock.called)

        # Assert files have been created
        self.assertTrue(os.path.exists(output_dir + hashlib.sha1(image_data).hexdigest()[:10] + '.jpg'))

    @patch('imagines.core.WebScrapper', WebScrapperMock)
    def test_dataset_augmentation_resize_images(self):
        """Unit tests for DataAugmentation"""

        # Load test image from disk
        with open('./tests/test_artifacts/test_image.jpg', 'rb') as f:
            image_data = f.read()

        dataset_augmentation = DatasetAugmentation(
            driver_type='chrome',
        )
        os.makedirs(self.tmp_dir + '/label')
        image_shape = (224, 224)

        image_file = io.BytesIO(image_data)
        image = Image.open(image_file).convert('RGB')
        image.save(self.tmp_dir + '/label/test.jpg')

        dataset_augmentation.resize_images(self.tmp_dir, image_shape)

        # Check image has been resized
        with open(self.tmp_dir + '/label/test.jpg', 'rb') as f:
            image_file = io.BytesIO(f.read())
        image = Image.open(image_file).convert('RGB')
        self.assertEqual(image.size, image_shape)
