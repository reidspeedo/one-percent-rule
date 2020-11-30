from lxml import html
import requests
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults
import json

zillow_data = ZillowWrapper('X1-ZWz17kc5du95aj_61q4u')

def clean(text):
    if text:
        return ''.join(''.join(text).split())
    return None


def get_headers():
    # Creating headers.
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'accept-encoding': 'gzip, deflate, sdch, br',
               'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
    return headers


def create_url(zipcode, filter):
    # Creating Zillow URL based on the filter.

    if filter == "newest":
        url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/days_sort".format(zipcode)
    elif filter == "cheapest":
        url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/pricea_sort/".format(zipcode)
    else:
        url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(zipcode)
    print(url)
    return url


def save_to_file(response):
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
            save_to_file(response)
            continue
        else:
            save_to_file(response)
            return response
    return None

def parse(zipcode, filter=None):
    url = create_url(zipcode, filter)
    response = get_response(url)

    if not response:
        print("Failed to fetch the page, please check `response.html` to see the response received from zillow.com.")
        return None

    parser = html.fromstring(response.text)
    search_results = parser.xpath("//div[@id='grid-search-results']//script[1]//text()")[0]
    list_price = str(parser.xpath("//div[@id='grid-search-results']//article//div[@class='list-card-price']/text()")[0])

    json_data = json.loads(search_results)
    full_address_dict = json_data['address']
    streetAddress = full_address_dict['streetAddress']
    postalCode = full_address_dict['postalCode']

    deep_search_response = zillow_data.get_deep_search_results(streetAddress, postalCode, True)
    api_result = GetDeepSearchResults(deep_search_response)


    rentzestimate_amount = api_result.rentzestimate_amount


    string = f'Address: {streetAddress}, {postalCode} \nList Price: {list_price} \nRent Estimate: {rentzestimate_amount}'
    print(string)

    #     properties = {'address': address,
    #                   'city': city,
    #                   'state': state,
    #                   'postal_code': postal_code,
    #                   'price': price,
    #                   'facts and features': 'info',
    #                   'real estate provider': broker,
    #                   'url': property_url,
    #                   'title': title}
    #     if is_forsale:
    #         properties_list.append(properties)
    # return properties_list


if __name__ == "__main__":
    scraped_data = parse('45140', 'newest')