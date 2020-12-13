from lxml import html
import requests
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults
import json
import os
import logging
import traceback

from zip_codes.zip_list import zip_list
from navigatefilter import navigatefilter


logging.basicConfig(filename='../app.log', filemode='w', format='%(levelname)s - %(message)s')
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
    url = f'https://www.zillow.com/homes/{zipcode}_rb/'
    print(url)
    return url

def save_to_response_file(response):
    # saving response to `response.html`
    with open("../response.html", 'w') as fp:
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

def get_listings_for_zip(zipcode, filter='newest', limit=10):
    url = create_url(zipcode)

    response = get_response(url)
    if not response:
        logging.error("Failed to fetch the page, please check `response.html` to see the response received from zillow.com.")
        return None
    parser = html.fromstring(response.text)
    search_results = parser.xpath("//div[@id='grid-search-results']//script[1]//text()")
    list_prices = parser.xpath("//div[@id='grid-search-results']//article//div[@class='list-card-price']/text()")
    list_card_types = parser.xpath("//div[@id='grid-search-results']//article//div[@class='list-card-type']/text()")
    prop_urls = parser.xpath("//div[@id='grid-search-results']//article//a/@href")

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
                prop_url = str(prop_urls[key])

                properties = {'address': streetAddress,
                              'postal_code': postalCode,
                              'price': list_price,
                              'rent_estimate': rentzestimate_amount,
                              'url': prop_url}

                properties_list.append(properties)
                #print(properties)
            elif list_card_types[key] == 'New Construction':
                logging.warning(f'Address: {address_string} / Ignoring New Construction')
        except Exception as e:
            logging.warning(f'{address_string} / {e}')
            # logging.warning(traceback.format_exc())

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
    navigatefilter.initialize_filter()

    zip_list = ['45140','98109']
    one_percent_properties = {}

    for zip in zip_list:
        scrapedata = get_listings_for_zip(zip)
        satisfied_props = one_percent_rule(scrapedata)
        for i in satisfied_props:
            if i['one_percent_rule']['satisfy_one_percent']:
                print(i['url'],i['one_percent_rule'])

        print(str(satisfied_props))