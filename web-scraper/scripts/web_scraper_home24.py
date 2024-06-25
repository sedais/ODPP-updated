import requests
from bs4 import BeautifulSoup
import csv

url = 'https://www.home24.at/esstisch/?typeRoom=livingRoom&typeRoom=diningRoom'
base_url = 'https://www.home24.at/'

response = requests.get(url)

# Create or open a CSV file for writing
with open('../data/home24_base.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(['Product Name', 'Product Price', 'Product URL', 'Material'])

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product containers
        products = soup.find_all('div', attrs={'data-cnstrc-item-name': True})

        # Iterate through each product and get its details
        for product in products:
            name = product['data-cnstrc-item-name']
            price = product['data-cnstrc-item-price']
            product_link_tag = product.find('a', {'data-testid': 'product-card-inner-container'})

            if product_link_tag and 'href' in product_link_tag.attrs:
                product_href = product_link_tag['href']
                product_url = base_url + product_href

                print(f'Product Name: {name}')
                print(f'Product Price: {price}')
                print(f'Product URL: {product_url}')

                product_response = requests.get(product_url)

                if product_response.status_code == 200:
                    product_soup = BeautifulSoup(product_response.content, 'html.parser')

                    # Extract material information from the product page
                    material_info = []
                    material_sections = product_soup.find_all('div', class_='css-1g9qw47')

                    for section in material_sections:
                        header = section.find('div', class_='css-1tr9upv')
                        if header and 'Material' in header.text:
                            material_spans = section.find_all('span', class_='keyword')
                            materials = [span.text.strip() for span in material_spans]
                            material_info.extend(materials)

                    material_info = ", ".join(material_info) if material_info else "Material information not found"

                    # Print or store the additional product information
                    print(f'Material: {material_info}')
                    print(f'Fetched content for {name}')

                    # Write the product information to the CSV file
                    writer.writerow([name, price, product_url, material_info])
                else:
                    print(f'Failed to fetch {product_url}')
            else:
                print(f'No href found for product: {name}')
