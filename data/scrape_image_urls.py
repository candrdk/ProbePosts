import requests
from bs4 import BeautifulSoup
import csv as csv

# Will retry on timeout forever
def fetch_img_url(url):
    success = False
    while not success:
        try:
            response = requests.get(url, timeout=5)
            success = True
        except requests.exceptions.RequestException as e:
            print('timed out! retrying')

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    img_url = 'https://picsum.photos/512'

    for img in img_tags:
        img_url = img.get('src')
        if '/wp-content/uploads/wpforms' in img_url:
            break

    return img_url

with open('dataset_raw.csv', 'r', newline='', encoding='utf-8') as dataset, \
     open('image_urls.csv',  'w', newline='', encoding='utf-8') as img_urls:
    reader = csv.DictReader(dataset)
    img_urls.write("image_url\n")
    for i, row in enumerate(reader):
        print(f"Fetching image url for post {i}")
        img_urls.write(fetch_img_url(row['img_link']) + '\n')
