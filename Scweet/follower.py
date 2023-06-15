from Scweet.Scweet.user import get_users_following
import json
import random

# file_credentials_path = ".\Scweet\credentials.txt"
file_credentials_path = "/app/credentials.txt"
class ScweetScraper:
    def __init__(self, env_path=file_credentials_path):
        self.env_path = env_path
    def scrape_following(self, users, verbose=0, headless=False, wait=2):
        def read_credentials(file_path):
            credentials = []
            
            with open(file_path, 'r') as file:
                for line in file:
                    username, password, email = line.strip().split(',')
                    credentials.append((username, password, email))
            
            return credentials

        credentials = read_credentials(self.env_path)
        # Randomly select a username and password
        random_credentials = random.choice(credentials)
        random_username, random_password, random_email = random_credentials
        following = get_users_following(users=users, username=random_username, password=random_password, email=random_email, verbose=verbose, headless=headless, wait=wait)
        return following

    def save_to_file(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f)

    def load_from_file(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data

