from csv import DictReader, DictWriter
from datetime import datetime, timedelta
from random import randint

from random_username.generate import generate_username 
from werkzeug.security import generate_password_hash

import requests
from bs4 import BeautifulSoup

post_attributes = ['id', 'posted', 'date', 'time', 'country', 'state', 'city', 'duration', 'summary', 'img_url', 'lat', 'lng']
city_attributes = ['id', 'name']
state_attributes = ['id', 'name']
user_attributes = ['id', 'username', 'password_hash', 'country', 'city', 'state']

city_id = 0
cities = {'Tampa': city_id}

state_id = 0
states = {'Florida': state_id}

user_id = 0
users = [
    { 
        'id': user_id, 
        'username': 'FloridaMan', 
        'password_hash': generate_password_hash('ProbeMeDaddy'),
        'country': 'United States', 
        'city': city_id, 
        'state': state_id
    }
]

user_locations = {}

# Throws on timeout
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

def get_user_id(state, city):
    global user_id
    global user_locations
    global users

    if state == 'Florida':
        return 0
    else:
        if state in user_locations:
            (post_count, id) = user_locations[state]
            if post_count < randint(4, 16):
                user_locations[state][0] += 1
                return id
        else:
            user_id += 1
            user_locations[state] = (1, user_id)

            username = generate_username()[0]
            while list(filter(lambda u: u['username'] == username, users)) != []:
                print('Repeated username, generating a new one')
                username = generate_username()[0]

            users.append({
                'id': user_id,
                'username': username,
                'password_hash': generate_password_hash('dis'),
                'country': 'United States',
                'city': cities[city],
                'state': states[state]
            })

            return user_id


with open('dataset_raw.csv',   'r', newline='', encoding='utf-8') as file, \
     open('posts.csv', 'w', newline='', encoding='utf-8') as dataset:
    
    reader = DictReader(file)
    writer = DictWriter(dataset, fieldnames=post_attributes)
    writer.writeheader()

    for i, row in enumerate(reader):
        # Generate a random posted date
        date_spotted = datetime.strptime(row['date'], '%d/%m/%y')
        date_posted = date_spotted + timedelta(days=randint(0,7))

        # Fetch the img url
        img_url = fetch_img_url(row['img_link'])
        
        # If duration is empty, set to unknown
        duration = 'Unknown' if row['duration'] == '' else row['duration']

        # Add assign city/state uid if they dont have one yet
        if row['city'] not in cities:
            city_id += 1
            cities[row['city']] = city_id
        
        if row['state'] not in states:
            state_id += 1
            states[row['state']] = state_id

        # Poster
        poster_id = get_user_id(row['state'], row['city'])

        # Write the post to the csv file
        writer.writerow({
            'id': poster_id,
            'posted': date_posted.strftime('%d/%m/%y'),
            'date': row['date'],
            'time': row['time'],
            'country': 'United States',
            'state': states[row['state']],
            'city': cities[row['city']],
            'duration': duration,
            'summary': row['summary'],
            'img_url': img_url,
            'lat': row['lat'],
            'lng': row['lng']
        })

        print(f'Read post {i}')


with open('states.csv', 'w', newline='', encoding='utf-8') as file:
    writer = DictWriter(file, fieldnames=state_attributes)
    writer.writeheader()
    writer.writerows([{'id': states[state], 'name': state} for state in states])
    
with open('cities.csv', 'w', newline='', encoding='utf-8') as file:
    writer = DictWriter(file, fieldnames=city_attributes)
    writer.writeheader()
    writer.writerows([{'id': cities[city], 'name': city} for city in cities])

with open('users.csv', 'w', newline='', encoding='utf-8') as file:
    writer = DictWriter(file, fieldnames=user_attributes)
    writer.writeheader()
    writer.writerows(users)
