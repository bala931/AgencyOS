
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="AgencyOS API")
# Temporary in-memory storage
briefs = []
next_id = 1

class Brief(BaseModel):

    title: str = Field(min_length=1, max_length=100)

    description: str = Field(min_length=1, max_length=1000)

    @field_validator("title", "description", mode="before")
    @classmethod
    def validate_text(cls, value):

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Field cannot be empty or contain only spaces")

        return value


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
# Delete an existing brief
@app.delete(
    "/briefs/{brief_id}",
    status_code=200,
    responses={
        404: {"description": "Brief not found"}
    }
)
def delete_brief(brief_id: int):

    for index, brief in enumerate(briefs):

        if brief["id"] == brief_id:

            deleted_brief = briefs.pop(index)

            return {
                "message": "Brief deleted successfully",
                "brief": deleted_brief
            }

    raise HTTPException(
        status_code=404,
        detail="Brief not found"
    )