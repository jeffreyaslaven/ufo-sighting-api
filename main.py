from fastapi import FastAPI
from contextlib import asynccontextmanager
from data.initial_load import InitalLoad
from data.update_data import UpdateData
from service.get_sightings import GetSightings
from tinydb import TinyDB

# ENTER SESSION/FORM DATA HERE
national_ufo_form_string = ''
new_date_db = TinyDB('data/db/new_date.json')
data_db = TinyDB('data/db/data.json')
date_written_db = TinyDB('data/db/date_written.json')
initial_load = InitalLoad(national_ufo_form_string, new_date_db, data_db, date_written_db)
update_data = UpdateData(national_ufo_form_string, new_date_db, data_db, date_written_db)
get_sightings = GetSightings(data_db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if len(data_db.all()) == 0:
        initial_load.inital_load()
    else:
        print('DB populated. Skipping initial DB load')
    update_data.update_data()
    yield
    update_data.update_data()

app = FastAPI(lifespan=lifespan)
    
@app.get('/ufo-sightings')
async def get_sightings_endpoint(day: int=None, month: int=None, year: int=None, city: str=None, state: str=None, country: str=None):
    if day is None and month is None and year is None and city is None and state is None and country is None:
       return {'data': get_sightings.get_all_sightings()}
    else:
        return {'data': get_sightings.get_all_sightings_by_param(day, month, year, city, state, country)}

@app.post('/db')
async def force_db_update_endpoint():
    update_data.update_data(force_update=True)
    return {'result': 'Successfully forced DB update'}
