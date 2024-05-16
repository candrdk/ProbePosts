from csv import DictReader, DictWriter
from datetime import datetime, timedelta
from random import randint, choices

from random_username.generate import generate_username 
from werkzeug.security import generate_password_hash

import requests
from bs4 import BeautifulSoup

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
    img_url = 'https://friddo.dk/assets/favicon.svg'

    for img in img_tags:
        img_url = img.get('src')
        if '/wp-content/uploads/wpforms' in img_url:
            break

    return img_url

class Dataset():
    def __init__(self, path):
        self.dataset_path = path

        self.post_attributes = ['poster_id', 'posted', 'date', 'time', 'country', 'state', 'city', 'duration', 'summary', 'img_url', 'lat', 'lng']
        self.city_attributes = ['id', 'name']
        self.state_attributes = ['id', 'name']
        self.user_attributes = ['id', 'username', 'password_hash', 'country', 'state', 'city']

        self.city_id = 0
        self.cities = {'Tampa': self.city_id}

        self.state_id = 0
        self.states = {'FL': self.state_id}

        self.user_id = 0
        self.users = [
            { 
                'id': self.user_id, 
                'username': 'FloridaMan', 
                'password_hash': generate_password_hash('ProbeMeDaddy'),
                'country': 'United States', 
                'city': self.city_id, 
                'state': self.state_id
            }
        ]

        self.user_locations = {}

    def get_user_id(self, state, city):
        if state == 'FL':
            return 0

        if state in self.user_locations:
            (max_posts_left, id) = self.user_locations[state]
            if max_posts_left > 0:
                self.user_locations[state] = (max_posts_left - 1, id)
                return id
        
        # Create a new user
        self.user_id += 1

        # Determine how many posts this user should maximally have
        user_post_count = choices([1,2,4,6,8,10], weights=[0.25, 0.1, 0.35, 0.15, 0.1, 0.05])[0]
        self.user_locations[state] = (user_post_count, self.user_id)

        username = generate_username()[0]
        while list(filter(lambda u: u['username'] == username, self.users)) != []:
            print('Repeated username, generating a new one')
            username = generate_username()[0]

        self.users.append({
            'id': self.user_id,
            'username': username,
            'password_hash': generate_password_hash('dis'),
            'country': 'United States',
            'state': self.states[state],
            'city': self.cities[city]
        })

        return self.user_id

    def clean_dataset(self):
        with open(self.dataset_path, 'r', newline='', encoding='utf-8') as dataset, \
             open('posts.csv',       'w', newline='', encoding='utf-8') as posts:
            
            reader = DictReader(dataset)
            writer = DictWriter(posts, fieldnames=self.post_attributes)
            writer.writeheader()

            for i, row in enumerate(reader):
                # Generate a random posted date
                date_spotted = datetime.strptime(row['date'], '%m/%d/%y')
                date_posted = date_spotted + timedelta(days=randint(0,7))

                # Fetch the img url
                img_url = fetch_img_url(row['img_link'])
                
                # If duration is empty, set to unknown
                duration = 'Unknown' if row['duration'] == '' else row['duration']

                # Add assign city/state uid if they dont have one yet
                if row['city'] not in self.cities:
                    self.city_id += 1
                    self.cities[row['city']] = self.city_id
                
                if row['state'] not in self.states:
                    self.state_id += 1
                    self.states[row['state']] = self.state_id

                # Get the user id of the poster
                poster_id = self.get_user_id(row['state'], row['city'])

                # Write the post to the csv file
                writer.writerow({
                    'poster_id': poster_id,
                    'posted': date_posted.strftime('%d/%m/%y'),
                    'date': date_spotted.strftime('%d/%m/%y'),
                    'time': row['time'],
                    'country': 'United States',
                    'state': self.states[row['state']],
                    'city': self.cities[row['city']],
                    'duration': duration,
                    'summary': row['summary'],
                    'img_url': img_url,
                    'lat': row['lat'],
                    'lng': row['lng']
                })

                print(f'Read post {i}')

                if i > 49:
                    break

        with open('states.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.state_attributes)
            writer.writeheader()
            writer.writerows([{'id': self.states[state], 'name': state} for state in self.states])
            
        with open('cities.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.city_attributes)
            writer.writeheader()
            writer.writerows([{'id': self.cities[city], 'name': city} for city in self.cities])

        with open('users.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.user_attributes)
            writer.writeheader()
            writer.writerows(self.users)



dataset = Dataset('dataset_raw.csv')
dataset.clean_dataset()
