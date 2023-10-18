class GetSightings():
    def __init__(self, data_db):
        self.data_db = data_db

    def get_all_sightings(self):
        result = self._get_only_sightings_db()
        
        print(f'User requested all records, sending {len(result)} records.')
        return result
    
    def get_all_sightings_by_param(self, day, month, year, city, state, country):
        data = self._get_only_sightings_db()
        result = []
        for entry in data:
            if self._check_if_entry_matches_date(entry, day, month, year) and self._check_if_entry_matches_location(entry, city, state, country):
                result.append(entry)
        
        print(f'User requested records matching provided params, sending {len(result)} records.')
        return result

    def _get_only_sightings_db(self):
        data = self._load_db_to_memory()
        result = []
        for entry in data:
            result.extend(entry.get('data'))
        print(f'Records loaded from DB: {len(result)}')
        return result
    
    @staticmethod
    def _check_if_entry_matches_date(entry, day, month, year):
        result = []
        if day is None:
            result.append(True)
        else: 
            result.append(entry.get('day') == day)
        if month is None:
            result.append(True)
        else:
            result.append(entry.get('month') == month)
        if year is None:
            result.append(True)
        else:
            result.append(entry.get('year') == year)
        
        return all(result)
    
    @staticmethod
    def _check_if_entry_matches_location(entry, city, state, country):
        result = []
        if city is None:
            result.append(True)
        else: 
            result.append(entry.get('city') == city)
        if state is None:
            result.append(True)
        else:
            result.append(entry.get('state') == state)
        if country is None:
            result.append(True)
        else:
            result.append(entry.get('country') == country)
        
        return all(result)

    def _load_db_to_memory(self):
        return self.data_db.all()
