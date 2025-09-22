
from fastapi import FastAPI, UploadFile, Path, HTTPException
from pydantic import BaseModel
from typing import Annotated

import pandas as pd
import numpy as np
from io import StringIO


# Initialise the app
app = FastAPI(title="REST API in python using FastAPI - Alex Chitham")

# Define a statistics model to return from the /summary/{user_id} endpoint
class Statistics(BaseModel):
    maximum: float
    minimum: float
    mean: float

# Define state attribute to keep the CSV in memory after being uploaded
app.state.csv_data = None

# Endpoint for uploading the CSV file
@app.post("/upload", summary="Path operation for uploading the CSV file")
async def csv_upload(file: UploadFile):

    # Ensure the file is the correct type
    if file.filename.endswith(".csv"):

        # Read the contents of the file in binary
        contents = await file.read()
        
        # Decode the binary data to a string
        string_contents = contents.decode("utf-8")

        # Read the string data into a CSV dataframe and store in app state
        app.state.csv_data = pd.read_csv(StringIO(string_contents))

        # Success message
        return {"message": f"{file.filename} uploaded successfully"}

    else: 
        raise HTTPException(status_code=400, detail="Uploaded file is not a CSV file")


    
# Endpoint for getting statistics for a particular user
@app.get("/summary/{user_id}", summary="Path operation for getting statistics for a particular user")
async def get_stats(user_id: Annotated[int, Path(title="The ID of the user to calculate stats for")]) -> Statistics:

    # Check a CSV file has been uploaded before calling this endpoint
    if app.state.csv_data is not None:

        csv_data = app.state.csv_data

        # Check if the given user ID exists in the CSV file
        if not (csv_data["user_id"] == user_id).any():
            raise HTTPException(status_code=404, detail="User ID not found in CSV file")

        # Extract the transaction amounts for the user with the given user ID
        user_transactions = csv_data[csv_data["user_id"] == user_id]
        amounts = (user_transactions["transaction_amount"]).to_numpy()

        # Create a Statistics item to return, using the max, min, and mean
        stats = Statistics(maximum=np.max(amounts), minimum=np.min(amounts), mean=np.mean(amounts))

    else:
        raise HTTPException(status_code=400, detail="CSV file has not been uploaded") 

    return stats