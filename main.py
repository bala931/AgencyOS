
from fastapi import FastAPI

app = FastAPI(title="AgencyOS API")


@app.get("/")
def home():
    return {
        "message": "AgencyOS API is running",
        "status": "success"
    }
