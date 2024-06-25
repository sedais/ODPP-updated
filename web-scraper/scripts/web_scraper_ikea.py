import pandas as pd
import requests
from bs4 import BeautifulSoup
import json


def get_product_details(product_url):
    response = requests.get(product_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', {'id': 'pip-range-json-ld'})
        if script:
            product_data = json.loads(script.string)
            description = product_data.get('description', 'No description available')
            reviews = product_data.get('review', [])
            return description, reviews
    return 'No description available', []


def main():
    url = 'https://www.ikea.com/at/de/cat/esstische-21825/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', {'class': 'pip-product-compact'})

        data = []
        for product in products:
            product_name = product.get('data-product-name')
            product_price = product.get('data-price')
            product_link = product.find('a', href=True)['href']
            full_product_link = f"{product_link}"

            description, reviews = get_product_details(full_product_link)

            reviews_str = "; ".join([
                f"{review.get('author', {}).get('name', 'Anonymous')}: {review.get('reviewRating', {}).get('ratingValue', 'No rating')} stars - {review.get('reviewBody', 'No review body')}"
                for review in reviews])

            data.append({
                "Product Name": product_name,
                "Product Price (EUR)": product_price,
                "Product Link": full_product_link,
                "Description": description,
                "Reviews": reviews_str
            })

        df = pd.DataFrame(data)
        return df
    else:
        print("Failed to retrieve the page")
        return pd.DataFrame()


df = main()
print(df.head())
df.to_csv('ikea_dining_tables.csv', index=False)
print("Data has been saved to ikea_dining_tables.csv")
