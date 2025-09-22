
from fastapi.testclient import TestClient
from main import app
import os


# Initialise the client to test the app
client = TestClient(app)

# Function to test uploading a file of the incorrect type
def test_invalid_upload():

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")

    with open("README.md", "rb") as md_file:
        files = {"file": md_file}
        response = client.post("/upload", files=files)

    assert response.status_code == 400
    assert response.json() == {"detail": "Uploaded file is not a CSV file"}

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")


# Function to test uploading a file of the correct type
def test_valid_upload():
    
    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")

    with open("dummy_transactions.csv", "rb") as csv_file:
        files = {"file": csv_file}
        response = client.post("/upload", files=files)

    assert response.status_code == 200
    assert response.json() == {"message": "dummy_transactions.csv uploaded successfully"}

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")


# Function to test response if querying the data before uploading a CSV file
def test_get_stats_early_call():
    
    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")

    response = client.get("/summary/1")
    assert response.status_code == 400
    assert response.json() == {"detail": "CSV file has not been uploaded"}

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")
    

# Function to test passing in an invalid user ID
def test_get_stats_invalid_user():

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")

    with open("dummy_transactions.csv", "rb") as csv_file:
        files = {"file": csv_file}
        client.post("/upload", files=files)

    response = client.get("/summary/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "User ID not found in CSV file"}

    response = client.get("/summary/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User ID not found in CSV file"}

    response = client.get("/summary/1001")
    assert response.status_code == 404
    assert response.json() == {"detail": "User ID not found in CSV file"}

    response = client.get("/summary/hello123")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")


# Function to test the summary statistics calculations on test CSV file
def test_valid_get_stats():

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")

    with open("tests/test.csv", "rb") as csv_file:
        files = {"file": csv_file}
        response = client.post("/upload", files=files)

    assert response.status_code == 200
    assert response.json() == {"message": "test.csv uploaded successfully"}

    response = client.get("/summary/1")
    assert response.status_code == 200
    assert response.json() == {
        "maximum": 30.0,
        "minimum": 10.0,
        "mean": 20.0
    }

    response = client.get("/summary/2")
    assert response.status_code == 200
    assert response.json() == {
        "maximum": 15.0,
        "minimum": 5.0,
        "mean": 10.0
    }

    response = client.get("/summary/3")
    assert response.status_code == 200
    assert response.json() == {
        "maximum": 50.0,
        "minimum": 50.0,
        "mean": 50.0
    }

    response = client.get("/summary/4")
    assert response.status_code == 404
    assert response.json() == {"detail": "User ID not found in CSV file"}

    if os.path.exists("dummy_transactions.db"):
        os.remove("dummy_transactions.db")
