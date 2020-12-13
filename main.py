from fastapi import FastAPI, status
import uvicorn
from pydantic import BaseModel
from services import zillow_services

app = FastAPI()

class Property(BaseModel):
    address: str
    zip_code: str
    list_price: str
    rent_estimate: str
    url: str

@app.get("/properties/{zip_code}")
def retrieve_properties(zip_code):
    return zillow_services.retrieve_properties(zip_code)

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000)
