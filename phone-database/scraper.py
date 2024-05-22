import requests
from bs4 import BeautifulSoup
import json
import time

# Base URL of the PhoneDB website
base_url = 'https://phonedb.net'


# Function to scrape phone data from a single page
def scrape_phone_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract phone data (modify based on the actual HTML structure)
    phone_data = {}
    phone_data['name'] = soup.find('h1', class_='phone-title').text.strip()
    phone_data['specs'] = {}

    specs = soup.find_all('div', class_='spec-row')
    for spec in specs:
        key = spec.find('div', class_='spec-name').text.strip()
        value = spec.find('div', class_='spec-value').text.strip()
        phone_data['specs'][key] = value

    return phone_data


# Function to scrape all phone data
def scrape_all_phones():
    all_phones = []
    page_number = 1

    while True:
        page_url = f'{base_url}/phones?page={page_number}'
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        phone_links = soup.find_all('a', class_='phone-link')
        if not phone_links:
            break

        for link in phone_links:
            phone_url = f"{base_url}{link['href']}"
            phone_data = scrape_phone_page(phone_url)
            all_phones.append(phone_data)

        page_number += 1
        time.sleep(1)  # Be respectful with your requests

    return all_phones


# Scrape data and save to a file
all_phone_data = scrape_all_phones()
with open('phones_data.json', 'w') as file:
    json.dump(all_phone_data, file)

print("Data scraped and saved successfully.")