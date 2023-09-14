# UFO Sightings API

### Please Note: This project is not for profit. This is a side project to highlight my skills in API development. I do not claim ownership as my own in the data pulled from the National UFO Reporting Online Database.

### See 'Future considerations' below on how I would make this project better in the future

### Prerequisites:
* [Python](https://www.python.org) - Required install
* [Google Chrome](https://www.google.com/chrome/) - Optional install - Instructions will be based on it
* [Postman](https://www.postman.com/) - Optional install - Any API client will work too
* Understanding of Python
* Computer you can install Python packages

### How to run locally:
This project uses the following packages to run it locally:

* [FastAPI](https://fastapi.tiangolo.com)
* [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
* [Requests](https://pypi.org/project/requests/)

Run the following command to install dependencies required to run the API locally in your terminal/command prompt: 

```pip install -r requirements.txt```

Due to the data being pulled from [National UFO Reporting Center Online Database](https://nuforc.org/databank/) you will need to get a session/form data token from your browser. Using Google Chrome, navigate [here](https://nuforc.org/subndx/?id=p230910). Right click anywhere on the table, click 'Inspect' (commonly known as 'Developer Tools' on other browsers). A sidebar will open within your browser. On that sidebar, click the tab labled 'Network'. With the 'Network' tab open, click the refresh button on your browser. You will now see all the network transactions between your browser and the website. Find the event labled `admin-ajax.php?action=get_wdtable&table_id=1&wdt_var1=Posted&wdt_var2=230910` within the network tab. Click **once** to view the event details. Within the event details tab that just opened, click the tab labled 'Payload'. Under the heading 'Form Data' click the text 'view source' - if it is already opened in source mode, you will see the text 'view parsed' in this tab instead. Copy the **entire** text within this tab beginning with 'draw...' and ending with '...wdtNonce=insert_id_here' otherwise the application load/refresh functionality will not work. Take this token and navigate to the **main.py** file. Enter the text you just copied, as the value for the variable 'national_ufo_form_string' under the comment labled **ENTER SESSION/FORM DATA HERE**. 

Once the dependencies are installed, and you have entered the session/form information, to start the API locally you need to run:

```uvicorn main:app --reload```

This will start the API running locally on: `http://127.0.0.1:8000`. uvicorn will direct you to another endpoint in your terminal/command prompt if something is currently using port 8000.

To see the full API's functionality, and possible parameters, just navigate to `http://127.0.0.1:8000/docs` in a web browser while the app is running.

Congrats! The api is now running locally.

A good way to test it is working is to do a GET request using Postman on `http://127.0.0.1:8000/ufo-sightings` to get all the UFO sightings for the past six months. 

Depending on your machine, to stop the API running locally use the command for your machine to stop a running process in your terminal/command prompt.

### Endpoints

**/ufo-sightings**

_Allowed HTTP Method(s)_: GET

_Functionality_: Returns UFO sightings from the past 6 months. This includes a summary of the event, when it happened, and where it happened. This data is refreshed every 24hrs on API startup and shutdown.

_Parameters_:

* day
    - _Type_: Int
    - _Description_: Number value to represent day of month
* month
    - _Type_: Int
    - _Description_: Number value to represent month (i.e. September == 9)
* year
    - _Type_: Int
    - _Description_: 4 digit number value to represent year (i.e. 2023)
* state
    - _Type_: Str
    - _Description_: Two character String representing state (i.e. Georgia == GA)
* city
    - _Type_: Str
    - _Description_: String representing city of occurence (i.e. Atlanta)
* country
    - _Type_: Str
    - _Description_: String representing country (i.e. USA)

_Body_:
* None

**/db**

_Allowed HTTP Method(s)_: POST

_Functionality_: Forces a refresh of the UFO DB outside of the regular 24 hour interval check at the beginning of API start and shutdown.

_Parameters_: 
* None

_Body_:
* None

### Future considerations

* Add automated tests using Pytest and unittest. It has been tested extensively for functionality, and overall reliability, outside of using automated frameworks. This approach would however not be sustainable as the API scales/new functionality is added. 
* Use an actual NoSQL DB (i.e. MongoDB, DynamoDB) for storing the data as opposed to text files representing one.
* Consider deploying and configuring this api within a container (i.e. Docker).
* Automate the session/token process so the you don't have to manually go to the website to generate it.