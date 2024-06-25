import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
base_url = "https://www.grueneerde.com/de/produkte/moebel/esszimmer/ge-c-esstische.html"
product_base_url = "https://www.grueneerde.com/de/produkte/moebel/esszimmer"

# Function to fetch and parse the product page
def fetch_product_details(product_url):
    response = requests.get(product_url)
    product_html = response.content
    product_soup = BeautifulSoup(product_html, 'html.parser')

    # Extract product details
    product_details_section = product_soup.find('div', cms="product_details_description")
    product_details = product_details_section.get_text(separator=" ", strip=True) if product_details_section else "N/A"

    # Extract technical data
    technical_data_section = product_soup.find('div', cms="DynamischeAttributeAudPDP")
    technical_data = {}
    if technical_data_section:
        for group in technical_data_section.find_all('li'):
            heading = group.find('h3').text.strip() if group.find('h3') else "N/A"
            properties = {}
            for prop in group.find_all('li'):
                label_element = prop.find('span', class_='Label')
                value_element = prop.find('span', class_='Value')
                label = label_element.text.strip() if label_element else "N/A"
                value = value_element.text.strip() if value_element else "N/A"
                properties[label] = value
            technical_data[heading] = properties

    return {
        'product_details': product_details,
        'technical_data': technical_data
    }

# Make a request to the main webpage
response = requests.get(base_url)
html = response.content

# Parse the HTML content
soup = BeautifulSoup(html, 'html.parser')

products = []

# Find all product containers
product_containers = soup.find_all('div', class_='ProductTileCMSComponent')

for container in product_containers:
    label_element = container.find('div', class_='Label')
    label = label_element.text.strip() if label_element else 'N/A'

    # Extract original price
    original_price_element = container.find('div', class_='Original')
    original_price = original_price_element.get_text(separator=" ", strip=True) if original_price_element else 'N/A'

    # Extract reduced price
    reduced_price_element = container.find('div', class_='Price')
    reduced_price = reduced_price_element.get_text(separator=" ", strip=True) if reduced_price_element else 'N/A'

    product_link_element = container.find('a', href=True)
    if product_link_element:
        product_link = product_base_url + product_link_element['href'][1:]  # Remove the leading "." from the href
        product_details = fetch_product_details(product_link)
    else:
        product_link = 'N/A'
        product_details = {
            'product_details': 'N/A',
            'technical_data': 'N/A'
        }

    products.append({
        'label': label,
        'original_price': original_price,
        'reduced_price': reduced_price,
        'product_link': product_link,
        'product_details': product_details['product_details'],
        'technical_data': product_details['technical_data']
    })

# Create a DataFrame from the extracted product details
df = pd.DataFrame(products)

# Save the DataFrame to a CSV file
df.to_csv('product_details.csv', index=False)

# Display the DataFrame
print(df)
