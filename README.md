
# ImagineS

ImagineS (Image Engine Search) tool augments an image dataset by searching a series of queries in Google Images.

## Install

---

* Create a new Conda environment

    `conda create -n data_aug python=3.7`

* Activate environment

    `source activate data_aug`

* Install library

    `pip install imagines`

## Usage

---

**Example:** Download `apple` and `water` related images by adding the query searches that would belong to each class.

```python
from imagines import DatasetAugmentation
dataset_augmentation = DatasetAugmentation(
    driver_type='chrome',
    driver_path='path_to/chromedriver',
)
label_queries = {
    'apple': ['apple'],
    'water': ['water', 'water bottle'],
}
max_links_to_fetch = 3
sleep_between_interactions = 1
image_shape = (224, 224)
resize_images = True
output_dir = 'images/'

dataset_augmentation.augment_dataset(
    label_queries,
    output_dir,
    max_links_to_fetch,
    image_shape,
    resize_images,
    sleep_between_interactions
)
```

## License

---

[MIT License](LICENSE)