from lxml import html
import requests
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults
import json
import os
import logging
from zip_list import zip_list

logging.basicConfig(filename='app.log', filemode='w', format='%(levelname)s - %(message)s')
zillow_data = ZillowWrapper(os.environ['ZILLOW_API_KEY'])

def get_headers():
    # Creating headers.
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'accept-encoding': 'gzip, deflate, sdch, br',
               'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
    return headers


def create_url(zipcode):
    for item in zip_list:
        if item[0] == zipcode:
            city_url = item[1].lower()
            state_url = item[2].lower()
        else:
            continue
    url = f'https://www.zillow.com/{city_url}-{state_url}-{zipcode}/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-72.1198548988988%2C%22east%22%3A-72.03041932150622%2C%22south%22%3A42.57401567418149%2C%22north%22%3A42.622602193357395%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A58364%2C%22regionType%22%3A7%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22doz%22%3A%7B%22value%22%3A%227%22%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A14%7D'
    return url

def save_to_response_file(response):
    # saving response to `response.html`
    with open("response.html", 'w') as fp:
        fp.write(response.text)

def get_response(url):
    # Getting response from zillow.com.

    for i in range(5):
        response = requests.get(url, headers=get_headers())
        print("status code received:", response.status_code)
        if response.status_code != 200:
            # saving response to file for debugging purpose.
            save_to_response_file(response)
            continue
        else:
            save_to_response_file(response)
            return response
    return None

def get_listings_for_zip(zipcode, filter='newest', limit=5):
    url = create_url(zipcode)

    response = get_response(url)
    if not response:
        logging.error("Failed to fetch the page, please check `response.html` to see the response received from zillow.com.")
        return None
    parser = html.fromstring(response.text)
    search_results = parser.xpath("//div[@id='grid-search-results']//script[1]//text()")
    list_prices = parser.xpath("//div[@id='grid-search-results']//article//div[@class='list-card-price']/text()")
    list_card_types = parser.xpath("//div[@id='grid-search-results']//article//div[@class='list-card-type']/text()")
    properties_list = []

    for key, items in enumerate(search_results):
        json_data = json.loads(items)
        full_address_dict = json_data['address']
        streetAddress = full_address_dict['streetAddress']
        postalCode = full_address_dict['postalCode']
        address_string = f'Address: {streetAddress}, {postalCode}'

        exlude = ['New Construction', 'Lot / Land for sale']
        try:
            if list_card_types[key] not in exlude:
                deep_search_response = zillow_data.get_deep_search_results(streetAddress, postalCode, True)
                api_result = GetDeepSearchResults(deep_search_response)
                rentzestimate_amount = api_result.rentzestimate_amount
                list_price = str(list_prices[key])

                properties = {'address': streetAddress,
                              'postal_code': postalCode,
                              'price': list_price,
                              'rent_estimate': rentzestimate_amount}

                properties_list.append(properties)
                #print(properties)
            elif list_card_types[key] == 'New Construction':
                logging.warning(f'Address: {address_string} / Ignoring New Construction')
        except Exception as e:
            logging.error(f'{address_string} / {e}')

        if key == limit:
            break
    return properties_list

def one_percent_rule(full_properties_list):
    for prop in full_properties_list:
        one_percent_rule_dict = {}

        try:
            percentage = 100*float(prop['rent_estimate'])/float(prop['price'].replace('$', '').replace(',', ''))
            one_percent_rule_dict['percent'] = percentage
            if percentage >= 1:
                one_percent_rule_dict['satisfy_one_percent'] = True
            else:
                one_percent_rule_dict['satisfy_one_percent'] = False
        except Exception as e:
            one_percent_rule_dict['percent'] = 0
            one_percent_rule_dict['satisfy_one_percent'] = False

        prop['one_percent_rule'] = one_percent_rule_dict

    return full_properties_list

if __name__ == "__main__":
    scrapedata = get_listings_for_zip('45140')
    satisfied_props = one_percent_rule(scrapedata)

    print(str(satisfied_props))