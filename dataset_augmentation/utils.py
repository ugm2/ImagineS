from selenium import webdriver
import time
import requests
import hashlib
import os
import io
from PIL import Image
from tqdm import tqdm

op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome('./chromedriver', options=op)

def augment_dataset(label_queries_dict, num_images_per_class=10, resize=True, image_size=224):
    for label, queries in tqdm(label_queries_dict.items(), desc="Augmenting dataset"):
        num_images = round(num_images_per_class / len(queries))
        for query in queries:
            search_and_download(query, driver, label, num_images)
            if resize:
                resize_images_from_folder(os.path.join('./new_images', label), (image_size, image_size))

def fetch_image_urls(query:str, wd:webdriver, max_links_to_fetch:int=10, sleep_between_interactions:float=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    patience = 100
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
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
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                # print(f"Found: {len(image_urls)} image links, done!")
                break

        # move the result startpoint further down
        results_start = len(thumbnail_results)

        if previous_image_count == image_count:
            patience -= 1
            if patience == 0:
                # print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            patience = 100

    return image_urls

def persist_image(folder_path:str, url:str):
    try:
        image_content = requests.get(url, timeout=10).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        # print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

def search_and_download(search_term:str, wd:webdriver, label:str, number_images=5, target_path='./new_images'):
    target_folder = os.path.join(target_path, label)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    res = fetch_image_urls(search_term, wd, number_images, sleep_between_interactions=0.5)
        
    for elem in res:
        persist_image(target_folder,elem)

    return target_folder, target_path

def resize_images_from_folder(folder_path:str, size:tuple):
    for file in os.listdir(folder_path):
        try:
            img = Image.open(os.path.join(folder_path, file))
            img = img.resize(size)
            img.save(os.path.join(folder_path, file))
        except Exception as e:
            print(e)