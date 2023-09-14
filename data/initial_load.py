import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class InitalLoad():
    def __init__(self, source_form_data):
        self.source_form_data = source_form_data

    def inital_load(self):
        last_six_months = self._calculate_last_six_months()
        print(f'Loading data up to and including: {last_six_months}')
        data = requests.get('https://nuforc.org/webreports/ndxpost.html')
        soup = BeautifulSoup(data.content, 'html.parser')
        s = soup.find_all('td')
        data = []
        new_date = None
        number_of_records = 0
        for item in s[0::2]:
            encounters = []
            try:
                date_str = item.find('a', href=True).text.strip()
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if date_obj >= last_six_months:
                    link = item.find('a', href=True).get('href')
                    encounters.extend(self._get_data_details(link))
                    if new_date is None:
                        new_date = date_obj
                        with open('data/db/new_date.txt', 'w') as file:
                            file.write(json.dumps({'day': new_date.day, 'month': new_date.month, 'year': new_date.year, 'link': link}))
                    elif new_date <= date_obj:
                        with open('data/db/new_date.txt', 'w') as file:
                            file.write(json.dumps({'day': new_date.day, 'month': new_date.month, 'year': new_date.year, 'link': link}))
                    number_of_records = len(encounters) + number_of_records
                    data.append({'link': link, 'day': date_obj.day, 'month': date_obj.month, 'year': date_obj.year, 'data': encounters})
                else:
                    break
            except:
                date_str = item.find('a', href=True).text.strip()
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if date_obj >= last_six_months:
                    link = item.find('a', href=True).get('href')
                    data.append({'link': link, 'day': date_obj.day, 'month': date_obj.month, 'year': date_obj.year, 'data': None})
                else:
                    break
        print(f'Sucessfully loaded {number_of_records} records.')
        # Writing data to txt file to represent a DB 
        with open('data/db/data.txt', 'w') as file:
            file.write(json.dumps(data))
        # Writing current day and time so updates can be run/checked
        now = datetime.now()
        current_date = {'day': now.day, 'month': now.month, 'year': now.year, 'day': now.day, 'hour': now.hour, 'minute': now.minute}
        with open('data/db/date_written.txt', 'w') as file:
            file.write(json.dumps(current_date))

    def _get_data_details(self, table_id):
        last_six_months = self._calculate_last_six_months()
        table_id = table_id.split('p')[1]
        url = f"https://nuforc.org/wp-admin/admin-ajax.php?action=get_wdtable&table_id=1&wdt_var1=Posted&wdt_var2={table_id}"
        payload = self.source_form_data
        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest'
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()

        records_filtered = response.get('recordsFiltered')
        payload =  payload.replace('100', records_filtered)
        response = requests.request("POST", url, headers=headers, data=payload).json()

        data = []
        for entry in response.get('data'):
            try:
                if entry[1] == '' or entry[1] == None:
                    data.append({'day': None, 'month': None, 'year': None, 'city': None, 'state': None, 'country': None, 'summary': None})
                else:
                    date = datetime.strptime(entry[1], '%m/%d/%Y %H:%M').date()
                    if date >= last_six_months:
                        city = entry[2]
                        state = entry[3]
                        country = entry[4]
                        summary = entry[6]
                        data.append({'day': date.day, 'month': date.month, 'year': date.year, 'city': city, 'state': state, 'country': country, 'summary': summary})
            except:
                date = datetime.strptime(entry[1], '%m/%d/%Y %H:%M').date()
                date >= last_six_months
                if date >= last_six_months:
                    data.append({'day': None, 'month': None, 'year': None, 'city': None, 'state': None, 'country': None, 'summary': None})
        return data

    @staticmethod
    def _calculate_last_six_months():
        now = datetime.now()
        if now.month - 6 < 0:
            month = 12 - (now.month - 6)
            return datetime(year=now.year, month=month, day=now.day).date()
        else:
            return datetime(year=now.year, month=now.month - 6, day=now.day).date()

    if __name__ == "__main__":
        pass
    