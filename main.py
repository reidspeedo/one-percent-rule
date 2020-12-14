from fastapi import FastAPI, status
import uvicorn
from pydantic import BaseModel
from services import zillow_services
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Property(BaseModel):
    address: str
    postal_code: str
    price: str
    rent_estimate: str
    url: str

@app.get("/properties/{zip_code}")
def retrieve_properties(zip_code):
    return zillow_services.retrieve_properties(zip_code)

@app.post("/properties", status_code=status.HTTP_201_CREATED)
def create_property(property: Property):
    return zillow_services.create_property(dict(property))

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000)
