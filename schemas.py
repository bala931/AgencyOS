from pydantic import BaseModel, Field, field_validator

from models import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)

    @field_validator("title", "description")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty or contain only spaces")

        return value


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    status: TaskStatus

    @field_validator("title", "description")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty or contain only spaces")

        return value


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    brief_id: int

    model_config = {
        "from_attributes": True
    }