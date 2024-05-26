from csv import DictReader, DictWriter
from datetime import datetime, timedelta
from random import randint, choices

from random_username.generate import generate_username 
from werkzeug.security import generate_password_hash

state_name = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District Of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

class Dataset():
    def __init__(self, path):
        self.dataset_path = path

        self.post_attributes = ['poster_id', 'posted', 'date', 'time', 'state_code', 'city_id', 'duration', 'summary', 'img_url', 'lat', 'lng']
        self.city_attributes = ['name']
        self.state_attributes = ['code', 'name']
        self.user_attributes = ['display_name', 'handle', 'password_hash', 'state_code', 'city_id']
        self.follows_attributes = ['user_id', 'follows_id']

        self.city_id = 1
        self.cities = {'Tampa': self.city_id}

        self.user_id = 1
        self.users = [
            {
                'display_name': 'Florida Man 🦅',
                'handle': 'FloridaMan',
                'password_hash': generate_password_hash('ProbeMeDaddy'),
                'city_id': self.city_id,
                'state_code': 'FL'
            }
        ]

        self.user_locations = {}
        self.password_hash = generate_password_hash('dis')

    def get_user_id(self, state_code, city):
        if state_code == 'FL':
            return 1

        if state_code in self.user_locations:
            (max_posts_left, id) = self.user_locations[state_code]
            if max_posts_left > 0:
                self.user_locations[state_code] = (max_posts_left - 1, id)
                return id
        
        # Create a new user
        self.user_id += 1

        # Determine how many posts this user should maximally have
        user_post_count = choices([1,2,4,6,8,10], weights=[0.25, 0.1, 0.35, 0.15, 0.1, 0.05])[0]
        self.user_locations[state_code] = (user_post_count, self.user_id)

        handle = generate_username()[0]
        while list(filter(lambda u: u['handle'] == handle, self.users)) != []:
            print('Repeated handle, generating a new one')
            handle = generate_username()[0]

        self.users.append({
            'display_name': handle,
            'handle': handle,
            'password_hash': self.password_hash,
            'state_code': state_code,
            'city_id': self.cities[city]
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

                # Posts cant be made before the internet was even a thing /:
                if date_posted < datetime(2003, 6, 6):
                    date_posted = datetime(randint(2003, 2023), randint(1,12), randint(1,29))

                # Just use a dummy image url here
                img_url = "https://picsum.photos/512"
                
                # If duration is empty, set to unknown
                duration = 'Unknown' if row['duration'] == '' else row['duration']

                # Add assign city id if they dont have one yet
                if row['city'] not in self.cities:
                    self.city_id += 1
                    self.cities[row['city']] = self.city_id

                # Get the user id of the poster
                poster_id = self.get_user_id(row['state'], row['city'])

                # Write the post to the csv file
                writer.writerow({
                    'poster_id': poster_id,
                    'posted': date_posted.strftime('%d/%m/%y'),
                    'date': date_spotted.strftime('%d/%m/%y'),
                    'time': row['time'],
                    'state_code': row['state'],
                    'city_id': self.cities[row['city']],
                    'duration': duration,
                    'summary': row['summary'],
                    'img_url': img_url,
                    'lat': row['lat'],
                    'lng': row['lng']
                })

                if (i % 100) == 0:
                    print(f'Read {i} posts.')

        with open('states.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.state_attributes)
            writer.writeheader()
            writer.writerows([{
                'code': code,
                'name': state_name[code]
            } for code in state_name])

        with open('cities.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.city_attributes)
            writer.writeheader()
            cities_by_id = sorted(self.cities, key=self.cities.get)
            writer.writerows([{'name': city} for city in cities_by_id])

        with open('users.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.user_attributes)
            writer.writeheader()
            writer.writerows(self.users)

        with open('follows.csv', 'w', newline='', encoding='utf-8') as file:
            writer = DictWriter(file, fieldnames=self.follows_attributes)
            writer.writeheader()

            follows = []
            for user_id in range(1, len(self.users)):
                count = randint(1, 20) # TODO: 4 -> 20
                following = set([randint(1, self.user_id) for i in range(count)])
                following.discard(user_id)
                follows += [
                    {
                        'user_id': user_id,
                        'follows_id': follows_id
                    }
                    for follows_id in following
                ]

            writer.writerows(follows)


if __name__ == '__main__':
    dataset = Dataset('dataset_raw.csv')
    dataset.clean_dataset()
