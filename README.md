# REST API in python using FastAPI - Alex Chitham

## How to Run

### (1) Install Dependencies
- Move to the `Python-Rest-API` directory.
- Run `pip install -r requirements.txt`

### (2) Generate Transactions Data
- Run `python src/data_generation.py` to generate the `dummy_transactions.csv` file. 

### (3) To Run Unit Tests: 
- Run `pytest`

### (4) For Automatic Documentation and Testing of the API:
- Run `fastapi dev src/main.py` or `uvicorn src.main:app --reload` to start the server.
- See documentation at `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc` in your browser.


## Implementation Details

### `POST /upload`

- Using the `UploadFile` from `FastAPI` allows for the user to upload any file of their choosing. To ensure a CSV file is uploaded, I check for the `.csv` file extension at the end.
- After reading the contents as binary using `file.read()` there are many errors that can thrown, including decoding, database, and missing columns. Therefore the remaining logic for this function is contained within a try block, and errors are redirected to the relevant HTTP exception.
- I have chosen to use a `SQLite3` database to store the transactions. Although a million entries was small enough to be contained in memory, I opted for the database as the specification emphasised handling of large datasets. Additional functionality I considered was to add entries to the databases in chunks, rather than storing the entire dataset in a variable beforehand. However, I believed this was out of scope for this challenge.

### `GET /summary/{user_id}`

- Defined a `Statistics` model containing the stats that should be returned from this endpoint. This allows `Pydantic` to perform validation on the returned data.
- This endpoint should not be called before a CSV file has been uploaded. Therefore, we ensure the `dummy_transactions.db` file exists first before continuing.
- As before, database errors can occur in this function, so the bulk of the logic is contained within a try block, with an error redirected to an HTTP exception.
- Using the `SQLite3` database makes querying the database easy. Finding the necessary statistics is also very simple using the `MAX`, `MIN`, and `AVG` functions within the query.
- Includes additional validation on the user ID, raising an exception if there were no results from the query. 

### Unit Testing

- Files for testing are located in the `tests/` folder. It contains a `.py` file and small test `.csv` file used to check the validity of the statistical calculations.
- There are five test functions in total:
   - Two for `POST /upload`: One to test a valid input, and one for an invalid input.
   - Three for `GET /summary/{user_id}`: One to test calling it before `POST /upload`, one for an invalid user, and one for checking the statistics returned by the database queries.
- For all the tests, `dummy_transactions.db` is deleted from storage if present, both before and after the tests run. This is to ensure each test can run in isolation without being affected by files produced by earlier tests.
