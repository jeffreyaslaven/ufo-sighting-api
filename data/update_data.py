from itertools import filterfalse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class UpdateData():
    def __init__(self, source_form_data, new_date_db, data_db, date_written_db):
        self.source_form_data = source_form_data
        self.new_date_db = new_date_db
        self.data_db = data_db
        self.date_written_db = date_written_db

    def update_data(self, force_update=False):
        if force_update:
            print('User forced DB update initiated.')

        data = self.date_written_db.all()[0]
        
        current_date = datetime.now()
        amount_of_time_passed = current_date - datetime(year=data.get('year'), month=data.get('month'), day=data.get('day'), minute=data.get('minute'), hour=data.get('hour'))

        if amount_of_time_passed.days >= 1 or force_update:
            print('Last data load is more than 24hrs old or forced update. Removing old data and adding new data')
            self._remove_old_records()
            self._add_new_records()
            current_date = {'day': current_date.day, 'month': current_date.month, 'year': current_date.year, 'day': current_date.day, 'hour': current_date.hour, 'minute': current_date.minute}
            self.date_written_db.truncate()
            self.date_written_db.insert(current_date)
        else:
            print('Outside of 24hr threshold. Skipping data update.')

    def _remove_old_records(self):
        db_data = self.data_db.all()
        self.data_db.truncate()
        
        print('Removing old tables.')
        prev_tables = len(db_data)
        db_data[:] = filterfalse(lambda x: self._is_data_not_too_old(x.get('day'), x.get('month'), x.get('year')), db_data)
        new_tables = len(db_data)
        print(f'Outdated tables removed: {prev_tables - new_tables}')
        
        print('Removing old records.')
        removed_records = 0
        for value in db_data:
            prev_size = len(value.get('data'))
            value['data'] = list(filterfalse(lambda x: self._is_data_not_too_old(x.get('day'), x.get('month'), x.get('year')), value.get('data')))
            new_size = len(value.get('data'))
            removed_records = (prev_size - new_size) + removed_records
        print(f'Removed total records {removed_records}')

        print('Writing any possible changes to table')
        self.data_db.insert_multiple(db_data)

    def _add_new_records(self):
        print('Checking for new data.')
        db_data = self.data_db.all()
        self.data_db.truncate()
        
        data = requests.get('https://nuforc.org/ndx/?id=post')
        soup = BeautifulSoup(data.content, 'html.parser')
        s = soup.find_all('td')
        latest_date = self.new_date_db.all()[0]
        latest_date = datetime(year=latest_date.get('year'), month=latest_date.get('month'), day=latest_date.get('day')).date()
        latest_date_new = None
        total_new_records = 0
        for item in s[0::2]:
            encounters = []
            try:
                date_str = item.find('a', href=True).text.strip()
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if latest_date >= date_obj:
                    break
                if date_obj >= latest_date:
                    link = item.find('a', href=True).get('href')
                    if latest_date_new is None:
                        latest_date_new = (date_obj, link)
                    elif date_obj == latest_date:
                        break
                    elif date_obj >= latest_date_new[0]:
                        latest_date_new = (date_obj, link)
                    encounters.extend(self._get_data_details(link))
                    total_new_records = total_new_records + len(encounters)
                    db_data.append({'link': link, 'day': date_obj.day, 'month': date_obj.month, 'year': date_obj.year, 'data': encounters})
            except:
                date_str = item.find('a', href=True).text.strip()
                print(f'Invalid value for record on date: {date_str}')
        
        if total_new_records > 0:
            print(f'Total number of new records: {total_new_records}')
            self.data_db.insert(db_data)
            self.new_date_db.truncate()
            self.new_date_db.insert({'day': latest_date_new[0].day, 'month': latest_date_new[0].month, 'year': latest_date_new[0].year, 'link': latest_date_new[1]})
        else:
            print('No new data found. Not appending new data to table.')

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

    def _is_data_not_too_old(self, day, month, year):
        date_to_filter = self._calculate_last_six_months()
        try:
            if datetime(year=year, month=month, day=day).date() >= date_to_filter:
                return False
            else:
                return True
        except:
            return True

    if __name__ == "__main__":
        pass
