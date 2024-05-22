import requests
from bs4 import BeautifulSoup
import pymongo


# Function to scrape iFixit data
def scrape_ifixit_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page with status code {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    phones = []

    # Find all phone blocks
    phone_blocks = soup.find_all('div', class_='wp-block-column is-layout-flow wp-block-column-is-layout-flow')

    for block in phone_blocks:
        try:
            # Extract phone name
            name = block.find('h1', class_='wp-block-heading has-text-align-center').text.strip()

            # Extract year
            year = block.find('p', class_='has-text-align-center has-normal-font-size').text.strip()

            # Extract pros
            pros_section = block.find('h6', text='PROS')
            pros_list = []
            if pros_section:
                pros = pros_section.find_next_sibling('ul', class_='has-normal-font-size').find_all('li')
                pros_list = [li.text.strip() for li in pros]

            # Extract cons
            cons_section = block.find('h6', text='CONS')
            cons_list = []
            if cons_section:
                cons = cons_section.find_next_sibling('ul', class_='has-normal-font-size').find_all('li')
                cons_list = [li.text.strip() for li in cons]

            # Extract repairability score
            #score_img = block.find('img', class_='wp-image-80960')
            #score_alt = score_img['alt'] if score_img else "No score available"
            #score = score_alt.split()[0] if score_img else "N/A"

            # Extract repairability score
            score_img = block.find('img', alt=lambda text: "Repairability Score" in text if text else False)
            score_alt = score_img['alt'] if score_img else "No score available"
            score = score_alt.split()[0] if score_img else "N/A"

            # Create phone data dictionary
            phone_data = {
                'name': name,
                'year': year,
                'pros': pros_list,
                'cons': cons_list,
                'repairability_score': score
            }

            phones.append(phone_data)
        except AttributeError as e:
            print(f"Error parsing block: {e}")
            continue

    return phones


# URL of the iFixit page
url = 'https://www.ifixit.com/repairability/legacy-smartphone-scores'
phone_data = scrape_ifixit_data(url)
