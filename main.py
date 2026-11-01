
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AgencyOS API")

# Request data structure
class Brief(BaseModel):
    title: str
    description: str

# Temporary storage
briefs = []
next_id = 1


@app.get("/")
def home():
    return {"message": "AgencyOS is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Create a client brief
@app.post("/briefs", status_code=201)
def create_brief(brief: Brief):
    global next_id

    new_brief = {
        "id": next_id,
        "title": brief.title,
        "description": brief.description
    }

    briefs.append(new_brief)
    next_id += 1

    return new_brief


# Retrieve all briefs
@app.get("/briefs")
def get_briefs():
    return briefs


# Retrieve one brief
@app.get("/briefs/{brief_id}")
def get_brief(brief_id: int):
    for brief in briefs:
        if brief["id"] == brief_id:
            return brief

    raise HTTPException(
        status_code=404,
        detail="Brief not found"
    )

# Update an existing brief
@app.put("/briefs/{brief_id}")
def update_brief(brief_id: int, updated_data: Brief):

    for brief in briefs:
        if brief["id"] == brief_id:

            brief["title"] = updated_data.title
            brief["description"] = updated_data.description

            return {
                "message": "Brief updated successfully",
                "brief": brief
            }

    raise HTTPException(
        status_code=404,
        detail="Brief not found"
    )
