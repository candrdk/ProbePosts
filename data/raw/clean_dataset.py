import os
from csv import DictReader, DictWriter

known_404 = [
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/8483F186-F115-413C-8753-3F018AC6EB2F-3991f21548560e00c72afff10f709f21.jpeg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/65FFE8D0-63A1-496F-9273-18455CFB1237-76c3b44ec73fda54fee789240b7b62dd.png",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/IMG_20211225_162036705_HDR2-fe34231db26f67bf3c3dbd0265864c12.jpg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/20211119_040144-539823a3a53b4495d744c75a0cb467ec.jpg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/952FD36B-9FDA-4601-A4C8-838D856443BA-c2db6f4b19405f386f8446069b749dc3.jpeg",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/Screen-Shot-2021-12-28-at-11.51.18-AM-df6bd75a4307ff868eb37b585303ec68.png",
    "https://nuforc.org/wp-content/uploads/wpforms/132-f1345440b16f33e415e847fc9d582913/20200811_231912-568f98f36cd058b4ef817aae093f6656.jpg"
]

dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(dir, 'dataset_raw.csv'),      'r') as raw_dataset_csv,            \
     open(os.path.join(dir, 'image_urls_raw.csv'),   'r') as raw_image_urls_csv,         \
     open(os.path.join(dir, '..', 'dataset.csv'),    'w', newline='') as dataset_csv,    \
     open(os.path.join(dir, '..', 'image_urls.csv'), 'w', newline='') as image_urls_csv:
    
    raw_dataset = DictReader(raw_dataset_csv)
    raw_image_urls = DictReader(raw_image_urls_csv)

    clean_dataset = DictWriter(dataset_csv, raw_dataset.fieldnames)
    clean_image_urls = DictWriter(image_urls_csv, raw_image_urls.fieldnames)

    clean_dataset.writeheader()
    clean_image_urls.writeheader()

    for report, img_url in zip(raw_dataset, raw_image_urls):
        is_image = img_url['image_url'].split('.')[-1] in ['png', 'jpg', 'jpeg']
        if is_image and img_url['image_url'] not in known_404:
            clean_dataset.writerow(report)
            clean_image_urls.writerow(img_url)
