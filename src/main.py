
from fastapi import FastAPI, UploadFile, Path, HTTPException
from pydantic import BaseModel
from typing import Annotated

import sqlite3
import csv
from io import StringIO
import os


# Initialise the app
app = FastAPI(title="REST API in python using FastAPI - Alex Chitham")

# Define a statistics model to return from the /summary/{user_id} endpoint
class Statistics(BaseModel):
    maximum: float
    minimum: float
    mean: float


# Endpoint for uploading the CSV file
@app.post("/upload", summary="Path operation for uploading the CSV file")
async def csv_upload(file: UploadFile):

    # Ensure the file is the correct type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a CSV file")

    # Read the contents of the file in binary
    contents = await file.read()

    try:
        # Decode the binary data
        string_contents = StringIO(contents.decode("utf-8"))

        # Read the file as CSV and temporarily store in memory
        csv_reader = csv.DictReader(string_contents)
        transactions = [
            (row["transaction_id"], int(row["user_id"]), int(row["product_id"]), row["timestamp"], float(row["transaction_amount"]))
            for row in csv_reader
        ]

        # Connect to SQLite database and create a cursor
        sqliteConnection = sqlite3.connect("dummy_transactions.db")
        cursor = sqliteConnection.cursor()

        # Create the table
        cursor.execute("""CREATE TABLE IF NOT EXISTS dummy_transactions (transaction_id TEXT, user_id INTEGER, 
                       product_id INTEGER, timestamp TEXT, transaction_amount REAL);""")
        
        # Insert all the rows into the table
        cursor.executemany("""INSERT INTO dummy_transactions (transaction_id, user_id, product_id, timestamp, 
                           transaction_amount) VALUES (?, ?, ?, ?, ?);""", transactions)
        
        # Commit changes to the database
        sqliteConnection.commit()
                                                                         

    # Catching all errors
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Decoding error: File encoding is not UTF-8")
    
    except sqlite3.Error:
        raise HTTPException(status_code=400, detail="Error with the internal database")
    
    except KeyError:
        raise HTTPException(status_code=400, detail="Table is missing some of the required rows")
    
    # Close the cursor and database
    finally:
        if cursor:
            cursor.close()   
        if sqliteConnection:
            sqliteConnection.close()
  

    # Success message
    return {"message": f"{file.filename} uploaded successfully"}
        


    
# Endpoint for getting statistics for a particular user
@app.get("/summary/{user_id}", summary="Path operation for getting statistics for a particular user")
async def get_stats(user_id: Annotated[int, Path(title="The ID of the user to calculate stats for")]) -> Statistics:

    # Check a CSV file has been uploaded before calling this endpoint
    if not os.path.exists("dummy_transactions.db"):
        raise HTTPException(status_code=400, detail="CSV file has not been uploaded") 

    try:
        # Connect to SQLite database and create a cursor
        sqliteConnection = sqlite3.connect("dummy_transactions.db")
        cursor = sqliteConnection.cursor()

        # Query the database, finding the max, min and mean simultaneously
        cursor.execute("""SELECT MAX(transaction_amount), MIN(transaction_amount), AVG(transaction_amount) 
                       FROM dummy_transactions WHERE user_id = ?""", (user_id,))
        
        # Store the queried results in new variables
        (max, min, mean) = cursor.fetchone()

        # Check if the user ID was found in the file
        if max is None:
            raise HTTPException(status_code=404, detail="User ID not found in CSV file")

    # Catching database error
    except sqlite3.Error:
        raise HTTPException(status_code=400, detail="Error with the internal database")
    
    # Close the cursor and database
    finally:
        if cursor:
            cursor.close()   
        if sqliteConnection:
            sqliteConnection.close()

    # Create a Statistics item to return, using the max, min, and mean
    stats = Statistics(maximum=max, minimum=min, mean=mean)

    return stats