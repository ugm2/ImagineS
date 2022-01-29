import hashlib
import io
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from typing import Dict, List, Tuple
from PIL import Image
import requests
import time
import os

import logging

from tqdm import tqdm

# Set up logging
logging.basicConfig(level=os.getenv("LOGGER_LEVEL", logging.WARNING))
logger = logging.getLogger("Dataset Augmentation classes")

class WebScrapper:

    def __init__(self, driver_type: str, driver_path: str):
        if driver_type == 'chrome':
            op = webdriver.ChromeOptions()
            op.add_argument('headless')
            ser = Service(driver_path)
            self.driver = webdriver.Chrome(service=ser, options=op)
        else:
            raise ValueError('Driver type not supported')

    def __scroll_to_end(self, sleep_between_interactions: float = 1):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    def search_images(self,
                      query: str,
                      max_links_to_fetch: int,
                      sleep_between_interactions: float = 1) -> set:

        # build the google query
        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

        self.driver.get(search_url.format(q=query))

        image_urls = set()
        image_count = 0
        results_start = 0
        patience = 100
        while image_count < max_links_to_fetch:
            self.__scroll_to_end(sleep_between_interactions)

            # get all image thumbnail results
            thumbnail_results = self.driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
            number_results = len(thumbnail_results)

            # print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
            previous_image_count = image_count
            for img in thumbnail_results[results_start:number_results]:
                # try to click every thumbnail such that we can get the real image behind it
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception:
                    continue

                # extract image urls    
                actual_images = self.driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        image_urls.add(actual_image.get_attribute('src'))

                image_count = len(image_urls)

                if len(image_urls) >= max_links_to_fetch:
                    logger.info(f"Found: {len(image_urls)} image links, done!")
                    break

                # move the result startpoint further down
                results_start = len(thumbnail_results)

                if previous_image_count == image_count:
                    patience -= 1
                    if patience == 0:
                        logger.info(f"Found: {len(image_urls)} image links, done!")
                        break
                else:
                    patience = 100

        return image_urls

class DatasetAugmentation:

    def __init__(self, driver_type: str, driver_path: str):
        self.driver = WebScrapper(driver_type, driver_path)

    def __persist_images(self, target_folder: str, image_urls: List[str]) -> None:

        for image_url in tqdm(image_urls, desc="Saving images"):
            try:
                image_content = requests.get(image_url, timeout=10).content
            except Exception as e:
                print(f"ERROR - Could not download {image_url} - {e}")

            try:
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert('RGB')
                file_path = os.path.join(target_folder, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
                with open(file_path, 'wb') as f:
                    image.save(f, "JPEG", quality=85)
            except Exception as e:
                print(f"ERROR - Could not save {image_url} - {e}")

    def resize_images(self,
                      folder_path: str,
                      image_shape: Tuple[int, int]) -> None:

        for label in os.listdir(folder_path):
            folder_path = os.path.join(folder_path, label)

            for image_file in tqdm(os.listdir(folder_path), desc="Resizing images"):
                file_path = os.path.join(folder_path, image_file)
                try:
                    image = Image.open(file_path)
                    image = image.resize(image_shape)
                    image.save(os.path.join(folder_path, image_file))
                except Exception as e:
                    print(f"ERROR - Could not resize image {file_path} - {e}")

    def augment_dataset(self,
                        label_queries: Dict[str, List[str]],
                        output_directory: str,
                        max_links_to_fetch: int,
                        image_shape: Tuple[int, int],
                        resize_images: bool = False,
                        sleep_between_interactions: float = 1) -> None:

        for label, queries in tqdm(label_queries.items(), desc="Augmenting dataset"):
            target_folder = os.path.join(output_directory, label)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            for query in queries:

                image_urls = self.driver.search_images(query=query,
                                                    max_links_to_fetch=max_links_to_fetch,
                                                    sleep_between_interactions=sleep_between_interactions)

                self.__persist_images(target_folder, image_urls)

                if resize_images:
                    self.resize_images(target_folder, image_shape)
