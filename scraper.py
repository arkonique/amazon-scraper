import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm


HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
}

def page_links(search_term,page):
    base_url = 'https://www.amazon.in/s?k='
    url = base_url + search_term + '&page=' + str(page)
    response = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for row in soup.find_all('div', class_='puis-card-container'):
        link = row.find('a', class_='a-link-normal')
        if link:
            links.append(link['href'])
    return links

def get_product(link):
    response = requests.get("https://www.amazon.in/" + link, headers=HEADER)
    soup = BeautifulSoup(response.text, 'html.parser')
    product = {}
    product['Title'] = get_title(soup)
    product['Price'] = get_price(soup)
    product['Rating'] = get_rating(soup)
    product['Link'] = "https://www.amazon.in/" + link
    product['Sales'] = get_sales(soup)
    product['Reviews'] = get_reviews(soup)
    return product

def get_title(soup):
    title = soup.find('span', id='productTitle').text
    return title.strip()

def get_price(soup):
    price = soup.find('span', class_='a-price-whole').text
    price = int(price.replace(',', '').strip().replace('.', ''))
    return price

def get_rating(soup):
    rating = float(soup.find('span', attrs={'data-hook' : 'rating-out-of-text'}).text.split()[0])
    return rating

def get_sales(soup):
    try:
        sales = int(soup.find('span', id='social-proofing-faceout-title-tk_bought').find('span').text.split()[0].replace('K', '000').replace('M', '000000').replace('+', ''))
    except AttributeError:
        sales = 'Not Available'
    return sales

def get_reviews(soup):
    reviews = int(soup.find('span', id='acrCustomerReviewText').text.split()[0].replace(',', ''))
    return reviews


def all_products(search_term, n):
    products = []
    for i in range(1, n+1):
        links = page_links(search_term,i)
        print(f'Page {i} of {n} pages, {len(links)} products found')
        for j in tqdm(range(len(links))):
            link = links[j]
            try:
                product = get_product(link)
                products.append(product)
            except AttributeError:
                continue
    return products

def all_products_in_range(search_term, n1,n2):
    products = []
    for i in range(n1, n2+1):
        links = page_links(search_term,i)
        print(f'Page {i} of {n1}-{n2} pages, {len(links)} products found')
        for j in tqdm(range(len(links))):
            link = links[j]
            try:
                product = get_product(link)
                products.append(product)
            except AttributeError:
                continue
    return products


search = sys.argv[1]
pages = sys.argv[2]
st = search.replace(' ', '_')

if sys.argv[1] == '-h' or sys.argv[1] == '--help' or len(sys.argv) == 1 or len(sys.argv) > 4:
    print('Usage: python grid_scraper.py <search_term> <number_of_pages>')
    print('Usage: python grid_scraper.py <search_term> -r <page_range>')
    print('Example: python grid_scraper.py "laptop" 5')
    print('Example: python grid_scraper.py "laptop" -r 1-5')
    sys.exit()
else:
    if sys.argv[2] == '-r':
        page1 = int(sys.argv[3].split('-')[0].strip())
        page2 = int(sys.argv[3].split('-')[1].strip())
        name = 'products' + '_' + st + '_' + str(page1) + '_' + str(page2) + '.xlsx'
        products = all_products_in_range(search,page1,page2)
    else:
        pages = int(sys.argv[2])
        products = all_products(search,pages)
        name = 'products' + '_' + st + '_' + str(pages) + '.xlsx'


    df = pd.DataFrame(products)
    df = df.drop_duplicates(subset='Title')
    print(df)
    df.to_excel(name, index=False)