from bs4 import BeautifulSoup
import re
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from urllib.request import urlopen, Request

"""In stock value must return as inStock before being passed to update database"""


def get_source_selenium(url):
    # Uses headless Chrome Browser to download wep page source HTML
    options = Options()
    #options.add_argument('--headless=new')
    options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36')
    # Disables image loading to lessen resource usage
    options.experimental_options['prefs'] = {
        'profile.managed_default_content_settings.images': 2
    }

    driver = webdriver.Chrome(
        options=options,
        service=ChromeService(ChromeDriverManager().install()))

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    driver.get(url)
    sleep(5)
    driver.find_element(By.ID, "onetrust-reject-all-handler").click()
    sleep(2)
    driver.find_element(By.XPATH,"/html/body/div[1]/div/div/section[1]/div/section/div/div/button").click()

    sleep(5)
    driver.find_element(By.ID, "show-more").click()
    sleep(2)
    return driver.page_source

def get_source_beatifulsoup(urls):
    # Uses headless Chrome Browser to download wep page source HTML
    url = urls
    hdrs = {'User-Agent': 'Mozilla'}
    website = urlopen(Request(url, headers=hdrs))
    html = BeautifulSoup(website, features="html.parser")
    text = html.prettify()
    return text

def scrape_website(website_urls, database, item_avail_key, item_name_key, item_url_key, extract_function, selenium):
    data = []
    count = 0

    if selenium == False:
        for website_url in website_urls:
            html_data = get_source_beatifulsoup(website_url)
            sleep(random.randint(1, 5))

            items = extract_function(html_data)
            data.extend(items)

    if selenium == True:
        for website_url in website_urls:
            html_data = get_source_selenium(website_url)

            items = extract_function(html_data)
            data.extend(items)

    if not data:
        sleep(30)
        data = scrape_website(website_urls, database, item_avail_key, item_name_key, item_url_key, extract_function, selenium)

    return data


def extract_combatcompany_data(data):

    items_dicts = []
    # Assuming your HTML content is stored in a variable called 'html_content'
    soup = BeautifulSoup(data, 'html.parser')
    # Find all list items with class 'grid__item'
    items = soup.find_all('li', class_='grid__item')

    for item in items:
        item_text = item.get_text(separator=' ')

        # Split the item text into a list of words
        words = item_text.split("  ")
        words = [item for item in words if item != ""]
        # The product name is the first word
        product_name = words[0]

        # The stock status is the second word
        stock_status = words[1]

        if stock_status != " Out of Stock":
            stock_status = "inStock"

        item_dict = {"Name": product_name, "Stock": stock_status}
        items_dicts.append(item_dict)
    return items_dicts


def extract_gamesworkshop_data(data):

    # Paste the HTML you provided here

    soup = BeautifulSoup(data, 'html.parser')

    # Find all product card elements
    product_cards = soup.find_all('div', {'data-test': 'product-card'})

    # Initialize lists to store the names and stock information
    item_dicts = []

    # Iterate through each product card
    for product_card in product_cards:
        # Extract the product name
        product_name_element = product_card.find('span',
                                                 class_='font-bold truncate text-marine-sm leading-7 text-Black-Primary-100')
        product_name = product_name_element.text if product_name_element else "Product name not available"
        product_url = product_card.find('a', class_='h-full product-card-image aspect-square')
        product_url = product_url.get('href')

        # Check for the presence of "Temporarily out of stock" and set the stock information accordingly
        if "Temporarily out of stock" in product_card.text:
            stock_info_text = "Temporarily out of stock"
        else:
            stock_info_text = "inStock"
        item_dict = {"Name": product_name, "Stock": stock_info_text, "URL": product_url}
        item_dicts.append(item_dict)

    return item_dicts


def extract_gapgames_data(data):
    # Define a regular expression pattern to match the desired fields
    pattern = r'"title":"(.*?)"[^{]*"handle":"(.*?)"[^{]*"available":(true|false)'

    # Use the findall method to extract matches
    matches = re.findall(pattern, data)

    # Create a list of items with "title" and "available" fields, excluding those with "Default Title"
    items = [{"title": match[0], "handle": match[1], "available": match[2] == "true"} for match in matches if
             match[0] != "Default Title"]
    items_dicts = [item for item in items if len(item["title"]) <= 50]
    for item in items_dicts:
        if item["available"] == True:
            item["available"] = "inStock"
    return items_dicts