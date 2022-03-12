import hashlib
import io
import json
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image
import requests
import time
import os

import logging

from tqdm import tqdm

# Set up logging
log_level = os.getenv("LOGGER_LEVEL", logging.WARNING)
logging.basicConfig(level=log_level)
logger = logging.getLogger("Dataset Augmentation classes")

class WebScrapper:

    def __init__(self, driver_type: str = 'chrome'):
        if driver_type == 'chrome':
            op = webdriver.ChromeOptions()
            op.add_argument('headless')
            ser = Service(ChromeDriverManager(log_level=log_level).install())
            self.driver = webdriver.Chrome(
                service=ser,
                options=op
            )
        else:
            raise ValueError('Driver type not supported')

    def __scroll_to_end(self, sleep_between_interactions: float = 1) -> None:
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

    def close_session(self):
        self.driver.quit()

class DatasetAugmentation:

    def __init__(self, driver_type: str = 'chrome'):
        self.driver = WebScrapper(driver_type)

    def _persist_images(self, target_folder: str, image_urls: List[str], return_images: bool = True) -> Optional[List]:

        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        images = [] if return_images else None

        for image_url in tqdm(image_urls, desc="Saving images"):
            try:
                image_content = requests.get(image_url, timeout=10).content

            except Exception as e:
                logger.warning(f"ERROR - Could not download {image_url} - {e}")

            try:
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert('RGB')
                if return_images:
                    images.append(image.copy())
                file_path = os.path.join(target_folder, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
                with open(file_path, 'wb') as f:
                    image.save(f)
                image.close()
            except Exception as e:
                logger.warning(f"ERROR - Could not save {image_url} - {e}")

        return images

    def _load_label_images(self, image_folder: str, max_images: int = None) -> List:
        images = []
        for image_filename in os.listdir(image_folder):
            image = Image.open(os.path.join(image_folder, image_filename)).convert('RGB')
            images.append(image.copy())
            image.close()
            if max_images is not None and len(images) >= max_images:
                break
        return images

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
                        label_queries: Union[Dict[str, List[str]], str],
                        output_directory: str,
                        max_links_to_fetch: int,
                        image_shape: Tuple[int, int],
                        resize_images: bool = False,
                        sleep_between_interactions: float = 1,
                        return_data: bool = True,
                        cache_data: bool = True) -> Optional[Tuple[List, List]]:

        images_list = [] if return_data else None
        labels_list = [] if return_data else None

        if isinstance(label_queries, str):
            # Load json file
            with open(label_queries, 'r') as f:
                label_queries = json.load(f)

        for label, queries in tqdm(label_queries.items(), desc="Augmenting dataset"):
            target_folder = os.path.join(output_directory, label)

            if os.path.exists(target_folder) and cache_data:
                logger.info(f"Found target folder {target_folder}. Loading images...")
                images = self._load_label_images(target_folder, max_links_to_fetch)
                images_list += images
                labels_list += [label] * len(images)
            else:
                if os.path.exists(target_folder) and not cache_data:
                    logger.info(f"Found target folder {target_folder}. Removing folder...")
                    shutil.rmtree(target_folder)
                for query in queries:

                    image_urls = self.driver.search_images(
                        query=query,
                        max_links_to_fetch=max_links_to_fetch,
                        sleep_between_interactions=sleep_between_interactions)

                    images = self._persist_images(target_folder, image_urls)

                    if return_data:
                        images_list.append(images)
                        labels_list.append(label)

            if resize_images:
                self.resize_images(output_directory, image_shape)

        self.driver.close_session()

        if return_data:
            return images_list, labels_list
