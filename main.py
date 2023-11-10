import grequests #load this before requests per documentation
import requests
from bs4 import BeautifulSoup
import urllib3

class TaxScrape():

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def extract_state_urls(main_url):
        response = requests.get(main_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        p_text = soup.findAll('p')
        urls = []
        for url in p_text:
            urls.append(url.find('a')['href'])
        return urls

    def locality_urls(state_url):
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        p_text = soup.findAll('table')
        locality_urls = []
        for url in p_text[0].findAll('a', href=True):
            locality_urls.append(url['href'])
        return locality_urls

    def generate_parcel_urls(locality_url, parcel_id_upper):
        parcels = []
        for parcel_id_num in range (1,parcel_id_upper+1):
            parcel_id = str(parcel_id_num)
            parcel_url = data[0]['connecticut']['locality_urls'][0]+f'Parcel.aspx?pid={parcel_id}'
            parcels.append(parcel_url)
        return parcels

    def get_parcel_page(parcel_urls):
        parcel_url_data = []
        rs = (grequests.get(parcel_url, verify = False, allow_redirects=False) for parcel_url in parcel_urls)
        responses = grequests.map(rs)
        for response in responses:
            temp_dict = {}
            url = response.url
            temp_dict['parcel_url'] = url
            temp_dict['status_code'] = response.status_code
            temp_dict['html_text'] = response.text
            parcel_url_data.append(temp_dict)
        return parcel_url_data

    def get_max_nonerror_parcel_id(parcel_data, sequential_non_200_limit):
        parcel_id = 0
        non_200_status_code_counter = 0
        for record in parcel_data:
            if non_200_status_code_counter > sequential_non_200_limit:
                break
            elif record['status_code'] != 200:
                non_200_status_code_counter += 1
            else:
                non_200_status_code_counter = 0
            parcel_id += 1
        max_parcel_id = parcel_id-sequential_non_200_limit-1
        return max_parcel_id

if __name__ =="main":
    main_url = 'https://www.vgsi.com/taxpayer-info/'
    tax_scrape = TaxScrape()
    state_urls = tax_scrape.extract_state_urls(main_url)

    data = []

    for state_url in state_urls:
        temp_dict = {}
        state = state_url.replace('https://www.vgsi.com/','').replace('-online-database/','')
        locality_urls_list = tax_scrape.locality_urls(state_url)
        temp_dict['state'] = state
        temp_dict['state_url'] = state_url
        temp_dict['locality_urls'] = locality_urls_list
        temp_dict['locality_data'] = []
        for locality_url in locality_urls_list:
            locality_data_dict = {}
            locality_data_dict['locality_url'] = locality_url
            locality_data_dict['html_text'] = {''}
            locality_data_dict['max_parcel_id'] = ''
            temp_dict['locality_data'].append(locality_data_dict)
        data.append(temp_dict)
